/**
 * Slack Socket Mode Listener for PM Copilot
 *
 * This app listens for /impact slash commands from Slack using Socket Mode,
 * which means NO public URL required - works entirely on localhost!
 *
 * Flow: Slack → Socket Mode → This app → Local services → GitHub PR → Slack notification
 */

const { App } = require('@slack/bolt');
const axios = require('axios');
require('dotenv').config();

// Initialize Slack app with Socket Mode
const app = new App({
  token: process.env.SLACK_BOT_TOKEN,        // xoxb-... (from OAuth & Permissions)
  appToken: process.env.SLACK_APP_TOKEN,     // xapp-... (from Basic Information)
  socketMode: true,                          // Enable Socket Mode (no public URL needed!)
});

// Configuration
const RIPGREP_API_URL = process.env.RIPGREP_API_URL || 'http://localhost:3001';
const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:8000';
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO_OWNER = process.env.REPO_OWNER || 'V-prajit';
const REPO_NAME = process.env.REPO_NAME || 'youareabsolutelyright';
const SLACK_CHANNEL = process.env.SLACK_CHANNEL || '#new-channel';

/**
 * Handle /relay slash command
 */
app.command('/relay', async ({ command, ack, respond, client }) => {
  // Acknowledge command immediately (Slack requires response within 3 seconds)
  await ack({
    response_type: 'in_channel',
    text: `⏳ Processing your request: "${command.text}"`
  });

  const featureRequest = command.text;
  const userId = command.user_id;
  const userName = command.user_name;
  const channelId = command.channel_id;

  console.log(`\n${'='.repeat(60)}`);
  console.log(`📨 Received /relay command from @${userName}`);
  console.log(`Feature request: "${featureRequest}"`);
  console.log(`${'='.repeat(60)}\n`);

  try {
    // Step 1: Search codebase with Ripgrep
    console.log('🔍 Step 1: Searching codebase with Ripgrep...');
    const ripgrepResponse = await axios.post(`${RIPGREP_API_URL}/api/search`, {
      query: featureRequest,
      path: './',
      type: 'all',
      case_sensitive: false
    });

    const ripgrepData = ripgrepResponse.data.data;
    const impactedFiles = ripgrepData.files || [];
    const isNewFeature = ripgrepData.is_new_feature || false;
    const totalFiles = ripgrepData.total || 0;

    console.log(`   ✅ Found ${totalFiles} file(s)`);
    console.log(`   📁 Files: ${impactedFiles.slice(0, 5).join(', ')}${totalFiles > 5 ? '...' : ''}`);
    console.log(`   🆕 New feature: ${isNewFeature}`);

    // Step 2: Generate PR with Snowflake Cortex
    console.log('\n🤖 Step 2: Generating PR with Snowflake Cortex...');
    const prResponse = await axios.post(`${BACKEND_API_URL}/api/snowflake/generate-pr`, {
      feature_request: featureRequest,
      impacted_files: impactedFiles,
      is_new_feature: isNewFeature,
      repo_name: `${REPO_OWNER}/${REPO_NAME}`
    });

    const prData = prResponse.data;
    console.log(`   ✅ Generated PR: "${prData.pr_title}"`);
    console.log(`   🌿 Branch: ${prData.branch_name}`);

    // Step 3: Create GitHub PR (if you want to auto-create)
    // For demo, you might skip this and just show the generated content
    let githubPrUrl = null;

    if (GITHUB_TOKEN && process.env.AUTO_CREATE_PR === 'true') {
      console.log('\n📝 Step 3: Creating GitHub PR...');

      try {
        const githubResponse = await axios.post(
          `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/pulls`,
          {
            title: prData.pr_title,
            body: prData.pr_description,
            head: prData.branch_name,
            base: 'main'
          },
          {
            headers: {
              'Authorization': `Bearer ${GITHUB_TOKEN}`,
              'Accept': 'application/vnd.github+json',
              'X-GitHub-Api-Version': '2022-11-28'
            }
          }
        );

        githubPrUrl = githubResponse.data.html_url;
        console.log(`   ✅ PR created: ${githubPrUrl}`);
      } catch (githubError) {
        console.error(`   ⚠️ GitHub PR creation failed: ${githubError.message}`);
        console.log('   ℹ️ Continuing without GitHub PR (you can create manually)');
      }
    } else {
      console.log('\n📝 Step 3: Skipping GitHub PR creation (set AUTO_CREATE_PR=true to enable)');
    }

    // Step 4: Send rich notification to Slack
    console.log('\n💬 Step 4: Sending notification to Slack...');

    const blocks = [
      {
        type: 'header',
        text: {
          type: 'plain_text',
          text: `✅ Task Created: ${prData.pr_title}`
        }
      },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*Feature Request:* ${featureRequest}\n*Requested by:* <@${userId}> (PM)`
        }
      },
      {
        type: 'section',
        fields: [
          {
            type: 'mrkdwn',
            text: `*Files Impacted:* ${totalFiles}`
          },
          {
            type: 'mrkdwn',
            text: `*Is New Feature:* ${isNewFeature ? 'Yes 🆕' : 'No 🔧'}`
          }
        ]
      },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*Impacted Files:*\n${impactedFiles.slice(0, 5).map(f => `• \`${f}\``).join('\n')}${totalFiles > 5 ? `\n• _...and ${totalFiles - 5} more_` : ''}`
        }
      },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*Branch:* \`${prData.branch_name}\``
        }
      }
    ];

    // Add PR description preview
    if (prData.pr_description) {
      blocks.push({
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*PR Description:*\n${prData.pr_description.substring(0, 300)}${prData.pr_description.length > 300 ? '...' : ''}`
        }
      });
    }

    // Add action buttons
    const actionElements = [];

    if (githubPrUrl) {
      actionElements.push({
        type: 'button',
        text: {
          type: 'plain_text',
          text: 'View PR'
        },
        url: githubPrUrl,
        style: 'primary'
      });
    }

    actionElements.push({
      type: 'button',
      text: {
        type: 'plain_text',
        text: 'View Repo'
      },
      url: `https://github.com/${REPO_OWNER}/${REPO_NAME}`
    });

    blocks.push({
      type: 'actions',
      elements: actionElements
    });

    // Add footer
    blocks.push({
      type: 'context',
      elements: [
        {
          type: 'mrkdwn',
          text: 'Powered by: *Snowflake Cortex (Mistral-Large)* • Generated with Slack Socket Mode'
        }
      ]
    });

    // Post to channel
    await client.chat.postMessage({
      channel: channelId,
      blocks: blocks,
      text: `✅ Task Created: ${prData.pr_title}` // Fallback text
    });

    console.log('   ✅ Notification sent to Slack!');
    console.log(`\n${'='.repeat(60)}`);
    console.log('✅ WORKFLOW COMPLETE!');
    console.log(`${'='.repeat(60)}\n`);

  } catch (error) {
    console.error('\n❌ ERROR:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    }

    // Send error notification to Slack
    await client.chat.postMessage({
      channel: channelId,
      blocks: [
        {
          type: 'header',
          text: {
            type: 'plain_text',
            text: '⚠️ PM Copilot Error'
          }
        },
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: `*Failed to process request:* "${featureRequest}"`
          }
        },
        {
          type: 'section',
          fields: [
            {
              type: 'mrkdwn',
              text: `*Error:*\n${error.message}`
            },
            {
              type: 'mrkdwn',
              text: `*Timestamp:*\n${new Date().toISOString()}`
            }
          ]
        },
        {
          type: 'context',
          elements: [
            {
              type: 'mrkdwn',
              text: 'Check backend services are running: `python run.py` and `npm run dev`'
            }
          ]
        }
      ],
      text: `⚠️ Error processing: ${featureRequest}`
    });
  }
});

/**
 * Start the app
 */
(async () => {
  try {
    await app.start();

    console.log('\n' + '='.repeat(60));
    console.log('⚡️ PM Copilot Slack Listener (Socket Mode)');
    console.log('='.repeat(60));
    console.log('Status: RUNNING ✅');
    console.log(`Ripgrep API: ${RIPGREP_API_URL}`);
    console.log(`Backend API: ${BACKEND_API_URL}`);
    console.log(`GitHub: ${REPO_OWNER}/${REPO_NAME}`);
    console.log('='.repeat(60));
    console.log('\nListening for /relay commands in Slack...');
    console.log('Press Ctrl+C to stop\n');
  } catch (error) {
    console.error('❌ Failed to start app:', error);
    process.exit(1);
  }
})();

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n📴 Shutting down gracefully...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n\n📴 Shutting down gracefully...');
  process.exit(0);
});
