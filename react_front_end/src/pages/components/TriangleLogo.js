import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import logo from "../../assets/vir-us_triangle_logo_white.jpeg";
import "./TriangleLogo.scss";

const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
    backgroundColor: "black",
    width: "100vw",
    height: "60vh",
    justifyContent: "center",
    flexDirection: "row",
    border: "1px dotted red",
  },
  image: {
    [theme.breakpoints.down("md")]: {
      width: "50vw",
    },
    [theme.breakpoints.up("md")]: {
      width: "30vw",
    },
    border: "1px dotted green",
  },
}));

export default function TriangleLogo(props) {
  const classes = useStyles();
  const dd = 78,
    hh = "06",
    mm = 26,
    ss = 47;
  return (
    <div className={classes.root}>
      <div className="statistics left">
        <div>
          <span>
            {dd} <br />
          </span>
          <span>DAYS</span>
        </div>
        <div>
          <span>
            {hh} <br />
          </span>
          <span>HOURS</span>
        </div>
      </div>

      <img src={logo} className={classes.image} />

      <div className="statistics right">
        <div>
          <span>
            {mm} <br />
          </span>
          <span>MINUTES</span>
        </div>
        <div>
          <span>
            {ss} <br />
          </span>
          <span>SECONDS</span>
        </div>
      </div>
    </div>
  );
}
