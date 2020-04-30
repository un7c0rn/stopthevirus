import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import "./GameStatistics.scss";

const useStyles = makeStyles((theme) => ({
  digits: {
    fontFamily: "Helvetica Neue",
    fontWeight: "bold",
    fontSize: "120%",
  },
  unit: {
    fontFamily: "Helvetica Neue",
    fontSize: "120%",
  },
}));

const dd = 78,
  hh = "06",
  mm = 26,
  ss = 47;

export const StatisticsLeft = ({ layout="column" }) => {
  const classes = useStyles();

  return (
    <div className={`statistics left ${layout}`}>
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
  );
};

export const StatisticsRight = ({ layout="column" }) => {
  const classes = useStyles();

  return (
    <div className={`statistics right ${layout}`}>
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
  );
};
