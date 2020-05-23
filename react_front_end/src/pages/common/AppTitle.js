import React, { useEffect } from "react";
import { makeStyles } from "@material-ui/core/styles";
import logo from "../../assets/vir-us.logo.type.white.letters.svg";
import { ReactComponent as Bg } from "../../assets/vir-us_world_map_transparent_canvas.svg";
import "./AppTitle.scss";
import "./Effects.scss";

const Map = () => {
  return <Bg />;
};

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

  const shuffle = (array) => {
    for (let i = array.length - 1; i > 0; i--) {
      let j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
  };

  useEffect(() => {
    const list = document.querySelectorAll("svg g g use");
    const iterate = () => {
      const nodes = shuffle([...list]).slice(0, 1000);
      while (nodes.length) {
        const node = nodes.pop();
        setTimeout(() => {
          node.classList.add("effect-fill");
        }, Math.random() * 2000);
      }
    };
    list.length && iterate();
  }, []);

  return (
    <div className={classes.root}>
      {/* <img src={Bg} className={classes.background} /> */}
      <Map className={classes.background} />
      <img src={logo} className="logo logo-animation" />
    </div>
  );
}
