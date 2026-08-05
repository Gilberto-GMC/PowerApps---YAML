const fs = require('fs');
const path = require('path');

const componentsDir = path.join(process.cwd(), 'components');
const files = fs.readdirSync(componentsDir).filter(f => f.endsWith('Module.tsx') || f.endsWith('Module_v2.tsx'));

for (const file of files) {
    const filePath = path.join(componentsDir, file);
    let content = fs.readFileSync(filePath, 'utf-8');

    // Find all <td>...</td> blocks
    content = content.replace(/<td([^>]*)>([\s\S]*?)<\/td>/g, (match, tdAttrs, tdContent) => {
        // Inside the td block, replace classNames
        let newContent = tdContent.replace(/className="([^"]*)"/g, (classMatch, classes) => {
            let newClasses = classes;
            
            // Skip dropdown menu items and absolute containers
            if (newClasses.includes('absolute') || newClasses.includes('w-full text-left')) {
                return classMatch;
            }
            
            // If it's a flex container
            if (newClasses.split(' ').includes('flex') || newClasses.split(' ').includes('inline-flex')) {
                if (newClasses.includes('flex-col')) {
                    // For flex-col, we need items-center to center horizontally
                    if (!newClasses.includes('items-center') && !newClasses.includes('items-end') && !newClasses.includes('items-start')) {
                        newClasses += ' items-center';
                    }
                } else {
                    // For row flex, we need justify-center to center horizontally
                    if (!newClasses.includes('justify-center') && !newClasses.includes('justify-end') && !newClasses.includes('justify-between') && !newClasses.includes('justify-start')) {
                        newClasses += ' justify-center';
                    }
                }
            }
            
            return `className="${newClasses}"`;
        });
        
        return `<td${tdAttrs}>${newContent}</td>`;
    });

    fs.writeFileSync(filePath, content);
    console.log(`Processed ${file}`);
}
