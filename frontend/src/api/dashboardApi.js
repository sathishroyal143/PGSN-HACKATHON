import axiosInstance from './axiosInstance'

const dashboardApi = {
  getDashboard: () => axiosInstance.get('/dashboard/'),
}

export default dashboardApi
