const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");

module.exports = function() {
  const yamlPath = path.join(__dirname, "_data/linkography.yaml");
  const fileContents = fs.readFileSync(yamlPath, "utf8");
  const linkography = yaml.load(fileContents);

  // Group data by category -> subcategory for the index tree
  const categoriesMap = {};
  linkography.forEach(item => {
    const cat = item.category || 'uncategorized';
    const sub = item.subcategory || 'general';
    
    if (!categoriesMap[cat]) {
      categoriesMap[cat] = { name: cat, items: [], subcategories: {} };
    }
    categoriesMap[cat].items.push(item);
    
    if (!categoriesMap[cat].subcategories[sub]) {
      categoriesMap[cat].subcategories[sub] = [];
    }
    categoriesMap[cat].subcategories[sub].push(item);
  });

  return {
    linkography,
    categoriesTree: categoriesMap
  };
};
