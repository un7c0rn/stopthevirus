import React from "react";
import { withStyles } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import Paper from "@material-ui/core/Paper";
import { maxButtonWidth } from "../../utilities/Constants";

const useStyles = makeStyles((theme) => ({
  root: {
    background: theme.background,
    color: "black",
    width: "100vw",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
  },
}));

const VerifiedPageInformation = () => {
  const classes = useStyles();

  return (
    <>
      <section className={classes.root}>
        <Paper square style={{ maxWidth: maxButtonWidth }}>
          <Typography
            gutterBottom
            className="page-information page-information-animation"
          >
            YOU'VE BEEN VERIFIED
          </Typography>
        </Paper>
      </section>
    </>
  );
};

export default withStyles(useStyles)(VerifiedPageInformation);
/*
      Can a global scale high stakes social game help inspire millions of
      Millennial and Gen-Z individuals across the world to engage in
      social distancing?
*/
