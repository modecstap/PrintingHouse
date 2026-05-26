import PropTypes from "prop-types";
import Modal from "../../../features/Modal/Modal";
import MultiLineCalculator from "../../NewCostCalculator/MultiLineCalculator";

const ItemModal = ({ item, onClose, hideActionButtons=true}) => (
  <Modal onClose={onClose} size="large">
    <MultiLineCalculator
      initial_data={item}
      hideActionButtons={hideActionButtons}
    />
  </Modal>
);

ItemModal.propTypes = {
  item: PropTypes.object.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default ItemModal;
