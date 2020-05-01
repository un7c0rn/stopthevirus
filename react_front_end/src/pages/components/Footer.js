import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import Button from "@material-ui/core/Button";
import Link from "@material-ui/core/Link";
import "./Footer.scss";

const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    "& > *": {
      width: "100vw",
      height: "10vh",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      padding: "1em 1em",
    },
  },
  paper: {
    backgroundColor: "transparent",
  },
}));

export default function Footer() {
  const classes = useStyles();

  const rules = (e) => {
    console.log("rules");
  };

  const preventDefault = (event) => event.preventDefault();

  return (
    <footer className={classes.root}>
      <Paper square className="footer">
        <div className="footer-links">
          <Link href="#" onClick={preventDefault}>
            Terms of service
          </Link>
          <Link href="#" onClick={preventDefault}>
            Privacy Policy
          </Link>
          <Link href="#" onClick={preventDefault}>
            Media
          </Link>
        </div>
        <Button variant="contained" onClick={rules}>
          rules
        </Button>
      </Paper>
    </footer>
  );
}
