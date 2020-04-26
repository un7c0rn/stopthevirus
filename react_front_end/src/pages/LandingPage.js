import { withStyles } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import React, { useContext, useEffect, useState } from "react";
import { AppContext } from "../App";
import Footer from "./components/Footer";
import LandingPageHeaderLogoSvg from "./components/LandingPageHeaderLogoSvg";
import LandingPageInformation from "./components/LandingPageInformation";
import "./LandingPage.scss";

const useStyles = makeStyles(() => ({
  root: {
    // background: theme.background,
    color: "white",
    height: "100vh",
    width: "100vw",
    display: "flex",
    flexDirection: "column",
    justifyContent: "flex-start",
  },
}));

const LandingPage = () => {
  const classes = useStyles();

  const { blurUi } = useContext(AppContext);

  const [blur, setBlur] = useState(false);

  useEffect(() => {
    setBlur(blurUi);
  }, [blurUi]);

  return (
    <>
      <section className={classes.root}>
        <div className={blur ? "landing-page blur" : "landing-page"}>
          <LandingPageHeaderLogoSvg />
          <LandingPageInformation />
          <Footer />
        </div>
      </section>
    </>
  );
};

export default withStyles(useStyles)(LandingPage);
