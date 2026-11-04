// .eleventy.js
const { execSync } = require("child_process");

module.exports = function(eleventyConfig) {
  // Pass through your CSS file to output folder
  eleventyConfig.addPassthroughCopy("style.css");

  // 1. Dynamic Current Year
  eleventyConfig.addShortcode("currentYear", () => {
    return new Date().getFullYear();
  });

  // 2. Automated Last Git Push/Commit Date
  eleventyConfig.addShortcode("lastGitCommitDate", () => {
    try {
      // Gets the last commit date in ISO format (YYYY-MM-DD)
      return execSync("git log -1 --format=%cd --date=format:'%Y-%m-%d'").toString().trim();
    } catch (e) {
      // Fallback if git isn't available in local directory
      return new Date().toISOString().split("T")[0];
    }
  });

  return {
    dir: {
      input: ".",
      includes: "_includes",
      output: "_site"
    }
  };
};
