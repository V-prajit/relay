import rg from '@vscode/ripgrep';

console.log('Default export:', rg);
console.log('Type:', typeof rg);
console.log('Is object?', typeof rg === 'object');
console.log('Keys:', Object.keys(rg));
