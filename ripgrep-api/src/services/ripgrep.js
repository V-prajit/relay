import { spawn } from 'child_process';
import rg from '@vscode/ripgrep';

const rgPath = rg.rgPath;

/**
 * Execute ripgrep search and return structured results
 * @param {string} query - Search query/pattern
 * @param {object} options - Search options
 * @returns {Promise<object>} Search results with files and matches
 */
export async function search(query, options = {}) {
  const {
    path = './',
    type = null,
    case_sensitive = false,
    max_results = 50,
  } = options;

  // Build ripgrep arguments
  const args = [
    '--json',                    // Output in JSON format
    '--max-count', String(max_results), // Limit results per file
  ];

  // Case sensitivity
  if (!case_sensitive) {
    args.push('--ignore-case');
  }

  // File type filter
  if (type) {
    args.push('--type', type);
  }

  // Add query and search path
  args.push(query, path);

  return new Promise((resolve, reject) => {
    const results = {
      files: [],
      matches: [],
      total: 0,
    };

    const rg = spawn(rgPath, args);

    let stdout = '';
    let stderr = '';

    rg.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    rg.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    rg.on('close', (code) => {
      // Code 0: matches found
      // Code 1: no matches (not an error)
      // Code 2: error occurred
      if (code === 2) {
        reject(new Error(`Ripgrep error: ${stderr}`));
        return;
      }

      if (code === 1 || !stdout.trim()) {
        // No matches found
        resolve(results);
        return;
      }

      // Parse JSON lines
      try {
        const lines = stdout.trim().split('\n');
        const filesSet = new Set();

        for (const line of lines) {
          if (!line.trim()) continue;

          const data = JSON.parse(line);

          // Handle match type
          if (data.type === 'match') {
            const match = data.data;
            const file = match.path.text;

            filesSet.add(file);

            results.matches.push({
              file,
              line: match.line_number,
              column: match.submatches[0]?.start || 0,
              content: match.lines.text.trim(),
              match_text: match.submatches[0]?.match?.text || '',
            });
          }
        }

        results.files = Array.from(filesSet);
        results.total = results.matches.length;

        resolve(results);
      } catch (error) {
        reject(new Error(`Failed to parse ripgrep output: ${error.message}`));
      }
    });

    rg.on('error', (error) => {
      reject(new Error(`Failed to spawn ripgrep: ${error.message}`));
    });
  });
}

/**
 * Get available file types supported by ripgrep
 * @returns {Promise<string[]>} List of supported file types
 */
export async function getSupportedTypes() {
  return new Promise((resolve, reject) => {
    const rg = spawn(rgPath, ['--type-list']);

    let stdout = '';

    rg.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    rg.on('close', (code) => {
      if (code !== 0) {
        reject(new Error('Failed to get ripgrep type list'));
        return;
      }

      const types = stdout
        .trim()
        .split('\n')
        .map(line => line.split(':')[0])
        .filter(Boolean);

      resolve(types);
    });

    rg.on('error', (error) => {
      reject(error);
    });
  });
}
