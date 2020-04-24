import React, { useRef, useEffect, useState } from "react";
import "./Preloader.scss";

export default function Preloader() {
  return (
    <div className="loader" role="progressbar">
      <span></span>
    </div>
  );
}
