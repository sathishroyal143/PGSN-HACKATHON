import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { fetchPatients } from '../../redux/slices/patientSlice'
import { getRecordSummary } from '../../api/medicalRecordsApi'

function PatientRecordSummaryCard({ patient }) {
  const navigate = useNavigate()
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getRecordSummary(patient.id)
      .then(res => {
        setSummary(res.data.data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [patient.id])

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-sm">
            {patient.first_name?.[0]}{patient.last_name?.[0]}
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{patient.first_name} {patient.last_name}</h3>
            <p className="text-sm text-gray-500">
              {patient.blood_group} · {patient.gender || 'Unknown'} · {patient.status}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg p-4 mb-4">
        <h4 className="text-xs font-semibold uppercase text-gray-500 tracking-wider mb-2">Medical Record Summary</h4>
        {loading ? (
          <p className="text-sm text-gray-400">Loading summary...</p>
        ) : summary ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
            <div>
              <p className="text-gray-500 text-xs">Total Records</p>
              <p className="font-medium">{summary.total_records || 0}</p>
            </div>
            <div>
              <p className="text-gray-500 text-xs">Consultations</p>
              <p className="font-medium">{summary.by_type?.CONSULTATION || 0}</p>
            </div>
            <div>
              <p className="text-gray-500 text-xs">Lab Reports</p>
              <p className="font-medium">{summary.by_type?.LAB_REPORT || 0}</p>
            </div>
            <div>
              <p className="text-gray-500 text-xs">Prescriptions</p>
              <p className="font-medium">{summary.by_type?.PRESCRIPTION || 0}</p>
            </div>
          </div>
        ) : (
          <p className="text-sm text-gray-400">No summary available.</p>
        )}
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate(`/family/patients/${patient.id}/records`)}
          className="flex-1 bg-white border border-blue-600 text-blue-600 text-sm font-medium py-2 rounded-lg hover:bg-blue-50 transition-colors text-center"
        >
          View Records
        </button>
        <button
          onClick={() => navigate(`/family/patients/${patient.id}/records?action=new`)}
          className="flex-1 bg-blue-600 text-white text-sm font-medium py-2 rounded-lg hover:bg-blue-700 transition-colors text-center"
        >
          + Add Record
        </button>
      </div>
    </div>
  )
}

export default function MedicalRecordsHubPage() {
  const dispatch = useDispatch()
  const { list: patients, loading } = useSelector((s) => s.patient)

  useEffect(() => {
    if (!patients || patients.length === 0) {
      dispatch(fetchPatients())
    }
  }, [dispatch, patients])

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Medical Records</h1>
        <p className="text-sm text-gray-500 mt-1">Select a patient to view or add medical records.</p>
      </div>

      {loading && patients.length === 0 ? (
        <p className="text-gray-500 text-center py-8">Loading patients...</p>
      ) : patients.length === 0 ? (
        <div className="text-center py-16 bg-white border border-gray-200 rounded-xl">
          <p className="text-4xl mb-3">🗂️</p>
          <p className="font-medium text-gray-900">No patients found</p>
          <p className="text-sm text-gray-500 mt-1">Add a patient in the Patients tab first.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {patients.map(p => (
            <PatientRecordSummaryCard key={p.id} patient={p} />
          ))}
        </div>
      )}
    </div>
  )
}
