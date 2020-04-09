const nodeExternals = require("webpack-node-externals");

module.exports = {
  // mode: "development",
  externals: [nodeExternals()]
};
