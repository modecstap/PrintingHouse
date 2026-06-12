import PropTypes from "prop-types";
import Modal from "../../../features/Modal/Modal";

const ItemModal = ({ onClose, children }) => (
  <Modal onClose={onClose} size="large">
    {children}
  </Modal>
);

ItemModal.propTypes = {
  onClose: PropTypes.func.isRequired,
  children: PropTypes.node.isRequired,
};

export default ItemModal;