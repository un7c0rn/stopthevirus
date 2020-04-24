import React from "react";
import FacebookIcon from "@material-ui/icons/Facebook";
import TwitterIcon from "@material-ui/icons/Twitter";
import InstagramIcon from "@material-ui/icons/Instagram";
import "./LandingPageSocialMediaIcons.scss";

const SocialMediaButton = ({ children }) => {
  return <div className="social-media-button">{children}</div>;
};

const LandingPageSocialMediaButtons = () => {
  return (
    <div className="social-media">
      <SocialMediaButton>
        <FacebookIcon />
      </SocialMediaButton>
      <SocialMediaButton>
        <InstagramIcon />
      </SocialMediaButton>
      <SocialMediaButton>
        <TwitterIcon />
      </SocialMediaButton>
    </div>
  );
};

export default LandingPageSocialMediaButtons;
