const fs = require('fs');
const path = require('path');

const filePath = path.join(process.cwd(), 'components', 'ConstructionEventsModule.tsx');
let content = fs.readFileSync(filePath, 'utf-8');

// Replace items-start with items-center in the specific td
content = content.replace(/<td className="px-6 py-4 text-center">\s*<div className="flex flex-col items-start">/g, '<td className="px-6 py-4 text-center">\n <div className="flex flex-col items-center">');

fs.writeFileSync(filePath, content);
