import PropTypes from "prop-types";
import Modal from "../../../features/Modal/Modal";
import CostCalculator from "../../CostCalculator/CostCalculator";

const ItemModal = ({ item, onClose, hideAcceptButtons=true}) => (
  <Modal onClose={onClose} size="large">
    <CostCalculator
      initial_data={item}
      hideAcceptButtons={hideAcceptButtons}
    />
  </Modal>
);

ItemModal.propTypes = {
  item: PropTypes.object.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default ItemModal;
