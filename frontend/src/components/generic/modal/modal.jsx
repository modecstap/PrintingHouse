import styles from "./modal.module.css";

const Modal = ({ children, onClose, size = "medium" }) => (
  <div className={styles.overlay} onClick={onClose}>
    <div
      className={`${styles.dialog} ${size === "large" ? styles.large : ""}`}
      onClick={(e) => e.stopPropagation()}
    >
      <button type="button" className={styles.close} onClick={onClose}>
        ✖
      </button>
      {children}
    </div>
  </div>
);

export default Modal;
