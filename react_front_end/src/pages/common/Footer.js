import React from "react";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";

import "./Footer.scss";

export default function Footer() {
  return (
    <footer className="footer">
      <Paper square>
        <Typography className="text ">
          <b>
            Rules: If the GLC, in its sole discretion, has authorized a Retailer
            to sell Tickets for On-Line Games at one or more of its Retailer
            Business Locations, in addition to all provisions, terms, and
            conditions of the Act, other Rules and Regulations, and the Retailer
            Contract, the On-Line Games Rules and Regulations herein shall apply
            to all On-Line Games. To the extent of any inconsistency with either
            the Retailer Contract or with the Retailer Rules and Regulations
            found in Chapter 2 of the GLC Policies and Procedures Manual, the
            On-Line Game Rules and Regulations shall govern the On-Line Games.
          </b>
          If the GLC, in its sole discretion, has authorized a Retailer to sell
          Tickets for On-Line Games at one or more of its Retailer Business
          Locations, in addition to all provisions, terms, and conditions of the
          Act, other Rules and Regulations, and the Retailer Contract, the
          On-Line Games Rules and Regulations herein shall apply to all On-Line
          Games. To the extent of any inconsistency with either the Retailer
          Contract or with the Retailer Rules and Regulations found in Chapter 2
          of the GLC Policies and Procedures Manual, the On-Line Game Rules and
          Regulations shall govern the On-Line Games.
        </Typography>
      </Paper>
    </footer>
  );
}
