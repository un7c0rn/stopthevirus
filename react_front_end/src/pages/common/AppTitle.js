import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import logo from "../../assets/vir-us.logo.type.white.letters.svg";
import background from "../../assets/vir-us_world_map_transparent_canvas.svg";
import "./AppTitle.scss";
import "./Effects.scss";

const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "flex-start",
    height: "auto",
    maxHeight: "40vh",
  },
}));

export default function AppTitle() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <img src={background} className="map-background" alt="map of the world" />
      <img src={logo} className="logo logo-animation" alt="logo" />
    </div>
  );
}
