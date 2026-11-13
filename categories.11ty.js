const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");

class SubcategoryPages {
  data() {
    const yamlPath = path.join(__dirname, "_data/linkography.yaml");
    const fileContents = fs.readFileSync(yamlPath, "utf8");
    const linkographyData = yaml.load(fileContents) || [];

    const groups = {};
    linkographyData.forEach(item => {
      const cat = item.category || 'uncategorized';
      const sub = item.subcategory || 'general';
      const key = `${cat}___${sub}`;
      if (!groups[key]) {
        groups[key] = { category: cat, subcategory: sub, items: [] };
      }
      groups[key].items.push(item);
    });

    // Sort items alphabetically (case-insensitive) within each subcategory group
    const subcategoriesList = Object.values(groups).map(group => {
      group.items.sort((a, b) => {
        const titleA = String(a.title || "").toLowerCase();
        const titleB = String(b.title || "").toLowerCase();
        return titleA.localeCompare(titleB);
      });
      return group;
    });

    return {
      layout: "layout.njk",
      pagination: {
        data: "subcategoriesList",
        size: 1,
        alias: "sub"
      },
      subcategoriesList,
      permalink: function(data) {
        const cat = this.slugify(data.sub.category);
        const sub = this.slugify(data.sub.subcategory);
        return `/categories/${cat}/${sub}/index.html`;
      },
      eleventyComputed: {
        title: function(data) {
          const cat = data.sub.category.replace(/-/g, ' ').toUpperCase();
          const sub = data.sub.subcategory.replace(/-/g, ' ').toUpperCase();
          return `// ${cat} > ${sub}`;
        }
      }
    };
  }

  render(data) {
    const { sub } = data;
    const catFormatted = sub.category.replace(/-/g, " ").toUpperCase();
    const subFormatted = sub.subcategory.replace(/-/g, " ").toUpperCase();

    let itemsHtml = sub.items.map(item => `
      <li class="link-item">
        <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="link-title">${item.title}</a>${item.annotation ? `:<br>` : ''}
        ${item.annotation ? `<span class="link-desc">${item.annotation}</span>` : ''}
      </li>
    `).join('');

    return `
      <div class="terminal-container">
        <p class="breadcrumb">
          <a href="/">&lt; RETURN TO MAIN DIRECTORY</a>
        </p>

        <h1>// ${catFormatted}</h1>
        <h2>&gt; ${subFormatted}</h2>
        <p class="meta-count">MATCHING RECORDS: ${sub.items.length}</p>

        <hr class="crt-line">

        <ul class="link-list">
          ${itemsHtml}
        </ul>

        <hr class="crt-line">

        <p class="breadcrumb">
          <a href="/">&lt; RETURN TO MAIN DIRECTORY</a>
        </p>
      </div>
    `;
  }
}

module.exports = SubcategoryPages;