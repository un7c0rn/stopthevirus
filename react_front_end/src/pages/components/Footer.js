import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import Button from "@material-ui/core/Button";
import Link from "@material-ui/core/Link";

const useStyles = makeStyles(theme => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    "& > *": {
      width: "100vw",
      height: "20vh",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      padding: "1em 1em"
    }
  },
  title: {
    margin: 0,
    fontSize: "4em"
  },
  links: {
    display: "flex",
    flexDirection: "column"
  },
  text: {textAlign:"justify",
  fontSize:"0.6rem" }
}));

export default function Footer() {
  const classes = useStyles();

  const rules = "If the GLC, in its sole discretion, has authorized a Retailer to sell Tickets for On-Line Games at one or more of its Retailer Business Locations, in addition to all provisions, terms, and conditions of the Act, other Rules and Regulations, and the Retailer Contract, the On-Line Games Rules and Regulations herein shall apply to all On-Line Games. To the extent of any inconsistency with either the Retailer Contract or with the Retailer Rules and Regulations found in Chapter 2 of the GLC Policies and Procedures Manual, the On-Line Game Rules and Regulations shall govern the On-Line Games.";

  const preventDefault = event => event.preventDefault();

  return (
    <footer className={classes.root}>
      <Paper square>
        <section className={classes.links}>
          <Typography className={classes.text}>
             <b> Rules:</b>{rules}

          </Typography>
        </section>
      </Paper>
    </footer>
  );
}
