import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import logo from "../../assets/vir-us_triangle_logo_white.svg";
import "./TriangleLogo.scss";
const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
    backgroundColor: "black",
    width: "100vw",
    height: "60vh",
    justifyContent: "center",
    flexDirection: "row",
  },
  image: {
    [theme.breakpoints.down("md")]: {
      width: "50vw",
    },
    [theme.breakpoints.up("md")]: {
      width: "30vw",

    },
    [theme.breakpoints.up("lg")]: {
      width: "25vw",
    },

  },
  digits: {
    fontFamily: "Helvetica Neue",
    fontWeight:"bold",
    fontSize: "120%"
},
  unit: {
    fontFamily: "Helvetica Neue",
    fontSize: "120%",
}
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
          <span className={classes.digits}>
            {dd} <br />
          </span>
          <span className={classes.unit}>DAYS</span>
        </div>
        <div>
          <span className={classes.digits}>
            {hh} <br />
          </span>
          <span className={classes.unit}>HOURS</span>
        </div>
      </div>

      <img src={logo} className={classes.image}
      style={{visibility: props.hideTriangle ? 'hidden' : '',
 }} />

      <div className="statistics right">
        <div>
          <span className={classes.digits}>
            {mm} <br />
          </span>
          <span className={classes.unit}>MINUTES</span>
        </div>
        <div>
          <span className={classes.digits}>
            {ss} <br />
          </span>
          <span className={classes.unit}>SECONDS</span>
        </div>
      </div>
    </div>
  );
}
