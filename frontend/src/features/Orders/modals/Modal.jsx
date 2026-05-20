import PropTypes from "prop-types";
import "./Modal.css";

const Modal = ({ children, onClose, size = "medium" }) => (
  <div className="modal-overlay" onClick={onClose}>
    <div
      className={`modal-content ${size}`}
      onClick={(e) => e.stopPropagation()} // предотвращаем закрытие при клике внутрь
    >
      <button className="modal-close" onClick={onClose}>
        ✖
      </button>
      {children}
    </div>
  </div>
);

Modal.propTypes = {
  children: PropTypes.node.isRequired,
  onClose: PropTypes.func.isRequired,
  size: PropTypes.oneOf(["small", "medium", "large"]),
};

export default Modal;
