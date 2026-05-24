import React, { useRef, useEffect, useState } from "react";

export default function AdvancedSection({ open, children }) {
  const ref = useRef(null);
  const [height, setHeight] = useState("0px");

  useEffect(() => {
    if (ref.current) {
      setHeight(open ? `${ref.current.scrollHeight}px` : "0px");
    }
  }, [open, children]);

  return (
    <div
      ref={ref}
      className="advanced-section"
      style={{
        maxHeight: height,
        opacity: open ? 1 : 0,
      }}
    >
      {children}
    </div>
  );
}
