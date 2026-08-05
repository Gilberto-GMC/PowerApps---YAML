const fs = require('fs');
const path = require('path');

const componentsDir = path.join(process.cwd(), 'components');
const files = fs.readdirSync(componentsDir).filter(f => f.endsWith('Module.tsx') || f.endsWith('Module_v2.tsx'));

for (const file of files) {
    const filePath = path.join(componentsDir, file);
    let content = fs.readFileSync(filePath, 'utf-8');

    // Replace text-left with text-center in table tags
    content = content.replace(/<table className="([^"]*)text-left([^"]*)"/g, '<table className="$1text-center$2"');

    // Replace text-left with text-center in th and td tags, or add text-center if neither is present
    content = content.replace(/<(th|td)([^>]*)className="([^"]*)"/g, (match, tag, beforeClass, classes) => {
        if (classes.includes('text-center') || classes.includes('text-right')) {
            return match;
        }
        if (classes.includes('text-left')) {
            return `<${tag}${beforeClass}className="${classes.replace('text-left', 'text-center')}"`;
        }
        return `<${tag}${beforeClass}className="${classes} text-center"`;
    });

    fs.writeFileSync(filePath, content);
    console.log(`Processed ${file}`);
}
