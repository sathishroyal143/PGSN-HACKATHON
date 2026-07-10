import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { fetchMembers, addMember, editMember, removeMember } from '../../redux/slices/familySlice'
import toast from 'react-hot-toast'

const RELATIONSHIPS = ['SELF','SPOUSE','PARENT','CHILD','SIBLING','GRANDPARENT','GRANDCHILD','UNCLE_AUNT','NEPHEW_NIECE','FRIEND','CAREGIVER','OTHER']

function MemberForm({ initial, onSave, onCancel, loading }) {
  const { register, handleSubmit, reset } = useForm({ defaultValues: initial || {} })
  useEffect(() => { reset(initial || {}) }, [initial])
  return (
    <form onSubmit={handleSubmit(onSave)} className="space-y-3 bg-gray-50 rounded-xl p-4 border border-gray-200">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">First Name</label>
          <input {...register('first_name', { required: true })} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Last Name</label>
          <input {...register('last_name', { required: true })} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Relationship</label>
          <select {...register('relationship')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
            {RELATIONSHIPS.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Date of Birth</label>
          <input {...register('date_of_birth')} type="date" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
        </div>
      </div>
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Phone</label>
        <input {...register('phone_number')} placeholder="+91XXXXXXXXXX" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
      </div>
      <div className="flex items-center gap-2">
        <input {...register('is_primary_patient')} type="checkbox" id="primary" className="rounded" />
        <label htmlFor="primary" className="text-sm text-gray-700">Primary Patient</label>
      </div>
      <div className="flex gap-2">
        <button type="submit" disabled={loading} className="bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-50">
          {loading ? 'Saving…' : 'Save'}
        </button>
        <button type="button" onClick={onCancel} className="text-sm text-gray-600 hover:text-gray-900 px-4 py-2 rounded-lg border border-gray-300">Cancel</button>
      </div>
    </form>
  )
}

export default function FamilyMembersPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { members, loading, error } = useSelector((s) => s.family)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState(null)

  useEffect(() => { dispatch(fetchMembers()) }, [dispatch])
  useEffect(() => { if (error) toast.error(error) }, [error])

  const handleAdd = async (data) => {
    const result = await dispatch(addMember(data))
    if (addMember.fulfilled.match(result)) { toast.success('Member added!'); setShowForm(false) }
  }

  const handleEdit = async (data) => {
    const result = await dispatch(editMember({ id: editing.id, data }))
    if (editMember.fulfilled.match(result)) { toast.success('Member updated!'); setEditing(null) }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this member?')) return
    const result = await dispatch(removeMember(id))
    if (removeMember.fulfilled.match(result)) toast.success('Member deleted.')
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <button onClick={() => navigate('/family/profile')} className="text-sm text-blue-600 hover:underline mb-1 block">← Family Profile</button>
          <h1 className="text-2xl font-bold text-gray-900">Family Members</h1>
        </div>
        <button onClick={() => { setShowForm(true); setEditing(null) }} className="bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
          + Add Member
        </button>
      </div>

      {showForm && !editing && (
        <div className="mb-4">
          <MemberForm onSave={handleAdd} onCancel={() => setShowForm(false)} loading={loading} />
        </div>
      )}

      {loading && members.length === 0 ? (
        <p className="text-gray-500">Loading…</p>
      ) : members.length === 0 ? (
        <p className="text-gray-500 text-sm">No family members added yet.</p>
      ) : (
        <div className="space-y-3">
          {members.map((m) => (
            <div key={m.id}>
              {editing?.id === m.id ? (
                <MemberForm initial={m} onSave={handleEdit} onCancel={() => setEditing(null)} loading={loading} />
              ) : (
                <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{m.full_name}</p>
                    <p className="text-sm text-gray-500">{m.relationship}{m.is_primary_patient ? ' · Primary Patient' : ''}</p>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => { setEditing(m); setShowForm(false) }} className="text-sm text-primary-600 hover:underline">Edit</button>
                    <button onClick={() => handleDelete(m.id)} className="text-sm text-red-500 hover:underline">Delete</button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
