import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { fetchContacts, addContact, editContact, removeContact } from '../../redux/slices/familySlice'
import toast from 'react-hot-toast'

const RELATIONSHIPS = ['SELF','SPOUSE','PARENT','CHILD','SIBLING','GRANDPARENT','GRANDCHILD','UNCLE_AUNT','NEPHEW_NIECE','FRIEND','CAREGIVER','OTHER']

function ContactForm({ initial, onSave, onCancel, loading }) {
  const { register, handleSubmit, reset } = useForm({ defaultValues: initial || {} })
  useEffect(() => { reset(initial || {}) }, [initial])
  return (
    <form onSubmit={handleSubmit(onSave)} className="space-y-3 bg-gray-50 rounded-xl p-4 border border-gray-200">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Full Name</label>
          <input {...register('name', { required: true })} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Relationship</label>
          <select {...register('relationship')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
            {RELATIONSHIPS.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Phone Number</label>
          <input {...register('phone_number', { required: true })} placeholder="+91XXXXXXXXXX" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Alternate Phone</label>
          <input {...register('alternate_phone')} placeholder="+91XXXXXXXXXX" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
        </div>
      </div>
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Email</label>
        <input {...register('email')} type="email" placeholder="contact@example.com" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
      </div>
      <div className="flex items-center gap-2">
        <input {...register('is_primary')} type="checkbox" id="primary_contact" className="rounded" />
        <label htmlFor="primary_contact" className="text-sm text-gray-700">Primary Contact</label>
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

export default function EmergencyContactsPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { contacts, loading, error } = useSelector((s) => s.family)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState(null)

  useEffect(() => { dispatch(fetchContacts()) }, [dispatch])
  useEffect(() => { if (error) toast.error(error) }, [error])

  const handleAdd = async (data) => {
    const result = await dispatch(addContact(data))
    if (addContact.fulfilled.match(result)) { toast.success('Contact added!'); setShowForm(false) }
  }

  const handleEdit = async (data) => {
    const result = await dispatch(editContact({ id: editing.id, data }))
    if (editContact.fulfilled.match(result)) { toast.success('Contact updated!'); setEditing(null) }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this contact?')) return
    const result = await dispatch(removeContact(id))
    if (removeContact.fulfilled.match(result)) toast.success('Contact deleted.')
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <button onClick={() => navigate('/family/profile')} className="text-sm text-blue-600 hover:underline mb-1 block">← Family Profile</button>
          <h1 className="text-2xl font-bold text-gray-900">Emergency Contacts</h1>
        </div>
        <button onClick={() => { setShowForm(true); setEditing(null) }} className="bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
          + Add Contact
        </button>
      </div>

      {showForm && !editing && (
        <div className="mb-4">
          <ContactForm onSave={handleAdd} onCancel={() => setShowForm(false)} loading={loading} />
        </div>
      )}

      {loading && contacts.length === 0 ? (
        <p className="text-gray-500">Loading…</p>
      ) : contacts.length === 0 ? (
        <p className="text-gray-500 text-sm">No emergency contacts added yet.</p>
      ) : (
        <div className="space-y-3">
          {contacts.map((c) => (
            <div key={c.id}>
              {editing?.id === c.id ? (
                <ContactForm initial={c} onSave={handleEdit} onCancel={() => setEditing(null)} loading={loading} />
              ) : (
                <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-medium text-gray-900">{c.name}</p>
                      {c.is_primary && <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full font-medium">Primary</span>}
                    </div>
                    <p className="text-sm text-gray-500">{c.relationship} · {c.phone_number}</p>
                    {c.email && <p className="text-xs text-gray-400">{c.email}</p>}
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => { setEditing(c); setShowForm(false) }} className="text-sm text-primary-600 hover:underline">Edit</button>
                    <button onClick={() => handleDelete(c.id)} className="text-sm text-red-500 hover:underline">Delete</button>
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
