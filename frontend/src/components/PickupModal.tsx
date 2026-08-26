import React, { useState } from 'react';
import { X, Calendar, Clock, CheckCircle2 } from 'lucide-react';
import { useCart } from '../context/CartContext';

interface PickupModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const dates = ['Today', 'Tomorrow', 'Day After'];
const slots = [
  '08:00 AM - 08:30 AM',
  '10:00 AM - 10:30 AM',
  '12:00 PM - 12:30 PM',
  '02:00 PM - 02:30 PM',
  '04:00 PM - 04:30 PM',
  '06:00 PM - 06:30 PM',
  '07:30 PM - 08:00 PM'
];

const PickupModal: React.FC<PickupModalProps> = ({ isOpen, onClose }) => {
  const { pickupSlot, setPickupSlot } = useCart();
  const [selectedDate, setSelectedDate] = useState(pickupSlot?.date || 'Today');
  const [selectedSlot, setSelectedSlot] = useState(pickupSlot?.time || '04:00 PM - 04:30 PM');

  if (!isOpen) return null;

  const handleSave = () => {
    setPickupSlot({ date: selectedDate, time: selectedSlot });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in">
      <div className="bg-cream-50 dark:bg-bakery-chocolate w-full max-w-md rounded-3xl p-6 shadow-2xl border border-amber-900/20 dark:border-amber-500/20 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-full hover:bg-amber-900/10 dark:hover:bg-cream-100/10 text-bakery-dark dark:text-cream-100"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-2xl bg-bakery-orange/20 text-bakery-orange flex items-center justify-center">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-serif text-xl font-bold">Schedule Takeaway Pickup</h3>
            <p className="text-xs text-gray-500 dark:text-amber-200/60">Choose your preferred fresh collection time</p>
          </div>
        </div>

        {/* Date Selector */}
        <div className="mb-5">
          <label className="block text-xs font-bold text-amber-950 dark:text-amber-200 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5" /> Select Pickup Date
          </label>
          <div className="grid grid-cols-3 gap-2">
            {dates.map((d) => (
              <button
                key={d}
                onClick={() => setSelectedDate(d)}
                className={`py-2 px-3 rounded-2xl text-xs font-semibold border transition ${
                  selectedDate === d
                    ? 'bg-bakery-orange text-white border-bakery-orange shadow-md'
                    : 'bg-white dark:bg-amber-950/40 border-amber-900/20 dark:border-amber-500/20 text-bakery-dark dark:text-cream-100 hover:border-bakery-orange'
                }`}
              >
                {d}
              </button>
            ))}
          </div>
        </div>

        {/* Time Slot Grid */}
        <div className="mb-6">
          <label className="block text-xs font-bold text-amber-950 dark:text-amber-200 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" /> Select Time Window
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-48 overflow-y-auto pr-1">
            {slots.map((s) => (
              <button
                key={s}
                onClick={() => setSelectedSlot(s)}
                className={`p-2.5 rounded-2xl text-xs text-left font-medium border flex items-center justify-between transition ${
                  selectedSlot === s
                    ? 'bg-bakery-brown text-white border-bakery-brown shadow'
                    : 'bg-white dark:bg-amber-950/40 border-amber-900/20 dark:border-amber-500/20 text-bakery-dark dark:text-cream-100 hover:border-bakery-orange'
                }`}
              >
                <span>{s}</span>
                {selectedSlot === s && <CheckCircle2 className="w-4 h-4 text-amber-300" />}
              </button>
            ))}
          </div>
        </div>

        {/* Confirm Button */}
        <button
          onClick={handleSave}
          className="w-full py-3 bg-gradient-to-r from-bakery-brown to-bakery-orange text-white font-bold text-sm rounded-2xl shadow-lg hover:opacity-95 transition"
        >
          Confirm Pickup Window
        </button>
      </div>
    </div>
  );
};

export default PickupModal;
