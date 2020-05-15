/* eslint-disable no-restricted-globals */
/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect, useState } from "react";
import Snackbar from "@material-ui/core/Snackbar";
import { makeStyles } from "@material-ui/core/styles";
import MuiAlert from "@material-ui/lab/Alert";

function Alert(props) {
  return <MuiAlert elevation={6} variant="filled" {...props} />;
}

const useStyles = makeStyles((theme) => ({
  root: {
    "& > div div": {
      justifyContent: "center",
    },
  },
}));

export default function Notification({ status }) {
  const classes = useStyles();

  const [state, setState] = useState({
    open: !isNaN(status),
    vertical: "top",
    horizontal: "center",
  });

  const { vertical, horizontal, open } = state;

  const handleClose = (event, reason) => {
    location.href = "/advert";
  };

  const getSnackBar = () => {
    if (status === 200) {
      return `Done!`;
    } else if (isNaN(status)) {
      return `There is a problem`;
    } else {
      return `?`;
    }
  };

  useEffect(() => {
    if (!isNaN(status)) {
      setState({
        open: !isNaN(status),
        vertical,
        horizontal,
      });
    }
  }, [status]);

  const getSeverity = () => {
    if (status === 200) {
      return "success";
    } else if (isNaN(status)) {
      return "error";
    } else return "warning";
  };

  return (
    !isNaN(status) && (
      <div className={classes.root}>
        <Snackbar
          anchorOrigin={{ vertical, horizontal }}
          key={`${vertical},${horizontal}`}
          open={open}
          onClose={handleClose}
          autoHideDuration={6000}
        >
          <Alert onClose={handleClose} severity={getSeverity()}>
            {getSnackBar()}
          </Alert>
        </Snackbar>
      </div>
    )
  );
}
