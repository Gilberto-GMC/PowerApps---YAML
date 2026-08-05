const fs = require('fs');
const path = require('path');

const componentsDir = path.join(process.cwd(), 'components');
const files = fs.readdirSync(componentsDir).filter(f => f.endsWith('Module.tsx') || f.endsWith('Module_v2.tsx'));

for (const file of files) {
    const filePath = path.join(componentsDir, file);
    let content = fs.readFileSync(filePath, 'utf-8');

    // Add mx-auto to w-fit inside <td> tags
    content = content.replace(/<td([^>]*)>([\s\S]*?)<\/td>/g, (match, tdAttrs, tdContent) => {
        let newContent = tdContent.replace(/className="([^"]*w-fit[^"]*)"/g, (classMatch, classes) => {
            if (!classes.includes('mx-auto')) {
                return `className="${classes} mx-auto"`;
            }
            return classMatch;
        });
        return `<td${tdAttrs}>${newContent}</td>`;
    });

    fs.writeFileSync(filePath, content);
}
