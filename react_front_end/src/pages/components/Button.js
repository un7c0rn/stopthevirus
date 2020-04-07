import React from "react";

export const Button = React.forwardRef(({ label, click }, ref) => (
  <button ref={ref} onClick={click}>
    {label}
  </button>
));
