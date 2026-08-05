const fs = require('fs');
const path = require('path');

const filePath = path.join(process.cwd(), 'components', 'LeakageModule.tsx');
let content = fs.readFileSync(filePath, 'utf-8');

content = content.replace(/text-xs font-bold text-slate-900 block/g, 'text-[13px] font-bold text-slate-900 block');

fs.writeFileSync(filePath, content);
