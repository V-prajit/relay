import simpleGit from 'simple-git';
import fs from 'fs';
import path from 'path';

const REPO_CLONE_URL = process.env.REPO_CLONE_URL || 'https://github.com/V-prajit/relay.git';
const REPO_CLONE_DIR = process.env.REPO_CLONE_DIR || '/tmp/ripgrep-repo-cache';
const REPO_BRANCH = process.env.REPO_BRANCH || 'main';
const REPO_CLONE_DEPTH = parseInt(process.env.REPO_CLONE_DEPTH || '1', 10);

/**
 * Check if the repository directory exists
 */
function repoExists() {
  return fs.existsSync(REPO_CLONE_DIR) && fs.existsSync(path.join(REPO_CLONE_DIR, '.git'));
}

/**
 * Ensure the repository is cloned and up-to-date
 * This function is called on server startup
 */
export async function ensureRepoCloned() {
  console.log('🔍 Checking repository status...');
  console.log(`   URL: ${REPO_CLONE_URL}`);
  console.log(`   Directory: ${REPO_CLONE_DIR}`);
  console.log(`   Branch: ${REPO_BRANCH}`);

  try {
    if (repoExists()) {
      console.log('📂 Repository directory exists, pulling latest changes...');
      await pullLatestChanges();
    } else {
      console.log('📥 Cloning repository for the first time...');

      // Create parent directory if it doesn't exist
      const parentDir = path.dirname(REPO_CLONE_DIR);
      if (!fs.existsSync(parentDir)) {
        fs.mkdirSync(parentDir, { recursive: true });
      }

      const git = simpleGit();
      await git.clone(REPO_CLONE_URL, REPO_CLONE_DIR, [
        '--branch', REPO_BRANCH,
        '--depth', REPO_CLONE_DEPTH.toString(),
        '--single-branch'
      ]);

      console.log('✅ Repository cloned successfully!');
    }

    // Log some stats about the cloned repo
    const git = simpleGit(REPO_CLONE_DIR);
    const log = await git.log(['-1']);
    if (log.latest) {
      console.log(`📌 Latest commit: ${log.latest.hash.substring(0, 7)} - ${log.latest.message}`);
      console.log(`👤 Author: ${log.latest.author_name}`);
      console.log(`📅 Date: ${log.latest.date}`);
    }

    return true;
  } catch (error) {
    console.error('❌ Error ensuring repository is cloned:', error.message);
    throw new Error(`Failed to clone/update repository: ${error.message}`);
  }
}

/**
 * Pull the latest changes from the remote repository
 */
export async function pullLatestChanges() {
  if (!repoExists()) {
    console.warn('⚠️  Repository does not exist, cannot pull. Run ensureRepoCloned first.');
    return false;
  }

  try {
    const git = simpleGit(REPO_CLONE_DIR);

    // Fetch and pull
    await git.fetch(['origin', REPO_BRANCH]);
    const pullResult = await git.pull('origin', REPO_BRANCH, ['--ff-only']);

    if (pullResult.summary.changes > 0) {
      console.log(`✅ Pulled ${pullResult.summary.changes} changes from remote`);
      console.log(`   Insertions: ${pullResult.summary.insertions}`);
      console.log(`   Deletions: ${pullResult.summary.deletions}`);
    } else {
      console.log('✅ Repository is already up-to-date');
    }

    return true;
  } catch (error) {
    console.error('❌ Error pulling latest changes:', error.message);
    return false;
  }
}

/**
 * Get the path to the cloned repository
 */
export function getRepoPath() {
  if (!repoExists()) {
    throw new Error(`Repository not cloned yet. Expected at: ${REPO_CLONE_DIR}`);
  }
  return REPO_CLONE_DIR;
}

/**
 * Get repository information (for health checks)
 */
export async function getRepoInfo() {
  try {
    if (!repoExists()) {
      return {
        cloned: false,
        path: REPO_CLONE_DIR,
        url: REPO_CLONE_URL,
        branch: REPO_BRANCH,
      };
    }

    const git = simpleGit(REPO_CLONE_DIR);
    const log = await git.log(['-1']);
    const status = await git.status();

    return {
      cloned: true,
      path: REPO_CLONE_DIR,
      url: REPO_CLONE_URL,
      branch: REPO_BRANCH,
      latestCommit: log.latest ? {
        hash: log.latest.hash,
        message: log.latest.message,
        author: log.latest.author_name,
        date: log.latest.date,
      } : null,
      status: {
        current: status.current,
        tracking: status.tracking,
        ahead: status.ahead,
        behind: status.behind,
      },
    };
  } catch (error) {
    console.error('Error getting repo info:', error.message);
    return {
      cloned: false,
      error: error.message,
    };
  }
}
