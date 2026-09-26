import { api } from './api.js';

export const adminService = {
  getAnalytics: (params = {}) => api.get('/admin/analytics', { params }),
  getOrders: () => api.get('/admin/orders'),
  updateOrderStatus: (orderId, status) => api.put(`/admin/orders/${orderId}/status`, { status }),
  markOrderPaid: (orderId) => api.put(`/admin/orders/${orderId}/payment`),
  createProduct: (payload) => api.post('/admin/products', payload),
  updateProduct: (productId, payload) => api.put(`/admin/products/${productId}`, payload),
  updateStock: (productId, stockQuantity) => api.put(`/admin/products/${productId}/stock`, { stock_quantity: stockQuantity }),
  deleteProduct: (productId) => api.delete(`/admin/products/${productId}`),
  getUsers: () => api.get('/admin/users'),
};
