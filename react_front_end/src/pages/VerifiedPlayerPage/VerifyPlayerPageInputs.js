import React, { useContext, useState } from "react";
import { withStyles } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import Button from "@material-ui/core/Button";
import { maxButtonWidth } from "../../utilities/Constants";
import { useParams } from "react-router-dom";
import { AppContext } from "../../App";
import Notification from "../common/Notification";

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
  title: {
    margin: "1em",
    fontSize: "3em",
    textAlign: "center",
  },
}));

const VerifyPlayerPageInputs = () => {
  const classes = useStyles();

  const { phone, code, game } = useParams();

  const {
    setNotificationOpen,
    setNotificationSuccess,
    // setNotificationError,
  } = useContext(AppContext);

  const [responseCode, setResponse] = useState();

  const submit = async (e) => {
    let url;

    if (process.env.REACT_APP_DEVELOPMENT_ENV === "development") {
      url = `/.netlify/functions/verify_code?phone=${phone}&code=${code}&game=${game}`;
    } else {
      url = `${process.env.WEBHOOK_REDIRECT_URL}/.netlify/functions/verify_code?phone=${phone}&code=${code}&game=${game}`;
    }

    console.log(url);

    const response = await fetch(url);

    console.log("verify player API reponse", response.status);

    setResponse(response.status);
  };

  return (
    <>
      <Notification status={responseCode} />
      <section className={classes.root}>
        <Paper square style={{ maxWidth: maxButtonWidth }}>
          <Button
            variant="contained"
            onClick={submit}
            style={{
              backgroundColor: "white",
              width: "100vw",
              maxWidth: maxButtonWidth,
              fontWeight: "bold",
              borderRadius: "0",
            }}
          >
            VERIFY ME
          </Button>
        </Paper>
      </section>
    </>
  );
};

export default withStyles(useStyles)(VerifyPlayerPageInputs);
/*
      Can a global scale high stakes social game help inspire millions of
      Millennial and Gen-Z individuals across the world to engage in
      social distancing?
*/
