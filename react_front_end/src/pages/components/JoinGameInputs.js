import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import MuiPhoneNumber from "material-ui-phone-number";
import {isSm} from "../../utilities/Utilities";
import React, { useRef, useState } from "react";

export default function JoinGameInputs() {
  const sm = isSm();
  const useStyles = makeStyles(theme => ({
    root: {
      backgroundColor:"black",
      display: "flex",
      flexWrap: "wrap",
      "& > *": {
        width: "100vw",
        //height: sm ? "40vh" : "35vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center"
      }
    },
    title: {
      margin: "1em 0",
      fontSize: "1em"
    },
    form: {
      display: "flex",
      flexDirection: "column",
      "& > *": {
        margin: "1em 0"
      }
    }
  }));
  const classes = useStyles();

  const tikTokRef = useRef();

 const [tikTok, setTikTok] = useState("");
 const [didSubmit, setDidSubmit] = useState(false);
 const [phone, setPhone] = useState("");
 const [country, setCountry] = useState({});

 const submit = event => {
   console.log("send to API endpoint");
   console.log(tikTokRef.current.value);
   console.log(phone);
   console.log(country);

   setDidSubmit(true);
 };

 function handleOnPhoneChange(value,countryObj) {
   setPhone(value);
   setCountry(countryObj);
}


  return (
    <div className={classes.root}>
      <Paper square>
        <form className={classes.form} autoComplete="off">
          <TextField
            id="join-game-inputs-tiktok"
            label="TIK TOK"
            variant="outlined"
            inputRef={tikTokRef}
            error={didSubmit && tikTok === ""}
            onChange={event => setTikTok(event.target.value )}
            value={tikTok}
          />
          <MuiPhoneNumber error={didSubmit && phone.length <= 6}
          label="PHONE NUMBER" defaultCountry={'us'} disableAreaCodes={true}
          onChange={handleOnPhoneChange}
          value={phone}
          id="join-game-inputs-phone"
          />
        </form>
        <form className={classes.form} autoComplete="off">

          <Button variant="contained" onClick={submit}
          style={{backgroundColor:'white',
                width:'100vw',
                fontWeight: 'bold',
            }}>
            JOIN THIS GAME
          </Button>
        </form>


      </Paper>
    </div>
  );
}
