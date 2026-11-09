import { useState } from "react";
import styles from "./tabs.module.css";

export function Tabs({ tabs }) {
  const [selected, setSelected] = useState(tabs[0].id);
  const [menuOpen, setMenuOpen] = useState(false);
  const { Content } = tabs.find((tab) => tab.id === selected);

  const selectTab = (id) => {
    setSelected(id);
    setMenuOpen(false);
  };

  return (
    <div className={styles.layout}>
      <nav
        className={`${styles.menu} ${menuOpen ? styles.menuOpen : ""}`}
        role="tablist"
        aria-orientation="vertical"
      >
        <button
          className={styles.burger}
          type="button"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen(!menuOpen)}
        >
          ☰
        </button>
        {tabs.map(({ id, label }) => (
          <button
            key={id}
            className={styles.tab}
            type="button"
            role="tab"
            aria-selected={id === selected}
            onClick={() => selectTab(id)}
          >
            {label}
          </button>
        ))}
      </nav>
      <div className={styles.content} role="tabpanel">
        <Content />
      </div>
    </div>
  );
}
