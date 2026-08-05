const fs = require('fs');
const path = require('path');

const componentsDir = path.join(process.cwd(), 'components');
const files = fs.readdirSync(componentsDir).filter(f => f.endsWith('Module.tsx') || f.endsWith('Module_v2.tsx'));

for (const file of files) {
    const filePath = path.join(componentsDir, file);
    let content = fs.readFileSync(filePath, 'utf-8');

    // Remove ml-5 inside <td> tags
    content = content.replace(/<td([^>]*)>([\s\S]*?)<\/td>/g, (match, tdAttrs, tdContent) => {
        let newContent = tdContent.replace(/ml-5/g, '');
        // Clean up double spaces
        newContent = newContent.replace(/  +/g, ' ');
        return `<td${tdAttrs}>${newContent}</td>`;
    });

    fs.writeFileSync(filePath, content);
}
