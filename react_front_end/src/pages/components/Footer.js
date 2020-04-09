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
      height: "10vh",
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
  text: { display: "flex", flexDirection: "column" }
}));

export default function Footer() {
  const classes = useStyles();

  const rules = e => {
    console.log("rules");
  };

  const preventDefault = event => event.preventDefault();

  return (
    <footer className={classes.root}>
      <Paper square>
        <section className={classes.links}>
          <Typography className={classes.text}>
            <Link href="#" onClick={preventDefault}>
              Terms of service
            </Link>
            <Link href="#" onClick={preventDefault}>
              Privacy Policy
            </Link>
            <Link href="#" onClick={preventDefault}>
              Social
            </Link>
          </Typography>
        </section>
        <Button variant="contained" onClick={rules}>
          rules
        </Button>
      </Paper>
    </footer>
  );
}
