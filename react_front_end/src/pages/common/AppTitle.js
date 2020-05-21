import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import logo from "../../assets/vir-us.logo.type.white.letters.svg";
import bg from "../../assets/vir-us_world_map_transparent_canvas.svg";
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
  background: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    position: "relative",
    zIndex: "2",
    alignSelf: "center",
    height: "100%",
    width: "100%",
  },
}));

export default function AppTitle() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <img src={bg} className={classes.background} />
      <img src={logo} className="logo logo-animation" />
    </div>
  );
}
