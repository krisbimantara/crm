<template>
  <LayoutHeader v-if="salesTeam.doc">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
  </LayoutHeader>
  <div v-if="salesTeam.doc" ref="parentRef" class="flex h-full">
    <Resizer
      v-if="salesTeam.doc"
      :parent="$refs.parentRef"
      class="flex h-full flex-col overflow-hidden border-r"
    >
      <div class="border-b">
        <div class="flex flex-col items-start justify-start gap-4 p-5">
          <div class="flex gap-4 items-center">
            <div class="group relative h-15.5 w-15.5">
              <Avatar
                size="3xl"
                class="h-15.5 w-15.5"
                :label="salesTeam.doc.nama"
              />
            </div>
            <div class="flex flex-col gap-2 truncate text-ink-gray-9">
              <div class="truncate text-2xl font-medium">
                <span>{{ salesTeam.doc.nama }}</span>
              </div>
              <div
                v-if="salesTeam.doc.cabang"
                class="flex items-center gap-1.5 text-base text-ink-gray-8"
              >
                <span class="">{{ salesTeam.doc.cabang }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div
        v-if="sections.data"
        class="flex flex-1 flex-col justify-between overflow-hidden"
      >
        <SidePanelLayout
          :sections="sections.data"
          doctype="CRM Sales"
          :docname="salesTeam.doc.name"
          @reload="sections.reload"
        />
      </div>
    </Resizer>
    <Tabs as="div" v-model="tabIndex" :tabs="tabs">
      <template #tab-item="{ tab, selected }">
        <button
          class="group flex items-center gap-2 border-b border-transparent py-2.5 text-base text-ink-gray-5 duration-300 ease-in-out hover:border-outline-gray-3 hover:text-ink-gray-9"
          :class="{ 'text-ink-gray-9': selected }"
        >
          <component v-if="tab.icon" :is="tab.icon" class="h-5" />
          {{ __(tab.label) }}
          <Badge
            class="group-hover:bg-surface-gray-7"
            :class="[selected ? 'bg-surface-gray-7' : 'bg-gray-600']"
            variant="solid"
            theme="gray"
            size="sm"
          >
            {{ tab.count }}
          </Badge>
        </button>
      </template>
      <template #tab-panel="{ tab }">
        <!-- Leads: hanya bulan berjalan (creation date) -->
        <LeadsListView
          v-if="tab.label === 'Leads' && rowsCurrentMonth.length"
          class="mt-4"
          :rows="rowsCurrentMonth"
          :columns="columns"
          :options="{ selectable: false, showTooltip: false }"
        />

        <!-- All Leads: semua leads milik Sales Team ini -->
        <LeadsListView
          v-else-if="tab.label === 'All Leads' && rows.length"
          class="mt-4"
          :rows="rows"
          :columns="columns"
          :options="{ selectable: false, showTooltip: false }"
        />

        <!-- List FID: data dari API eksternal -->
        <div v-else-if="tab.label === 'List FID'" class="mt-4">
          <div v-if="fidList.loading" class="text-base text-ink-gray-6">
            {{ __('Loading...') }}
          </div>

          <div v-else-if="fidList.error" class="text-base">
            <div class="font-medium text-red-600">
              {{ __('Failed to load List FID') }}
            </div>
            <div class="mt-2 text-sm text-ink-gray-6">
              {{ __('Kemungkinan masalah CORS. Aktifkan CORS pada endpoint, atau gunakan proxy backend untuk meneruskan request dari server.') }}
            </div>
          </div>

          <div
            v-else-if="fidData.length"
            class="overflow-auto rounded border"
          >
            <table class="min-w-full text-left">
              <thead>
                <tr>
                  <th
                    v-for="col in fidColumns"
                    :key="col"
                    class="border-b px-3 py-2 text-ink-gray-7"
                  >
                    {{ col }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(item, idx) in fidData"
                  :key="idx"
                  class="border-b"
                >
                  <td
                    v-for="col in fidColumns"
                    :key="col"
                    class="px-3 py-2"
                  >
                    {{ formatCell(item[col]) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div
            v-else
            class="grid flex-1 place-items-center text-xl font-medium text-ink-gray-4"
          >
            <div class="flex flex-col items-center justify-center space-y-3">
              <component :is="tab.icon" class="!h-10 !w-10" />
              <div>{{ __('No {0} Found', [__(tab.label)]) }}</div>
            </div>
          </div>
        </div>

        <!-- Fallback empty state untuk Leads / All Leads -->
        <div
          v-else
          class="grid flex-1 place-items-center text-xl font-medium text-ink-gray-4"
        >
          <div class="flex flex-col items-center justify-center space-y-3">
            <component :is="tab.icon" class="!h-10 !w-10" />
            <div>{{ __('No {0} Found', [__(tab.label)]) }}</div>
          </div>
        </div>
      </template>
    </Tabs>
  </div>
  <ErrorPage
    v-else-if="errorTitle"
    :errorTitle="errorTitle"
    :errorMessage="errorMessage"
  />
  <DeleteLinkedDocModal
    v-if="showDeleteLinkedDocModal"
    v-model="showDeleteLinkedDocModal"
    :doctype="'CRM Sales'"
    :docname="salesTeam.doc.name"
    name="SalesTeam"
  />
</template>

<script setup>
import ErrorPage from '@/components/ErrorPage.vue'
import Resizer from '@/components/Resizer.vue'
import Icon from '@/components/Icon.vue'
import SidePanelLayout from '@/components/SidePanelLayout.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import LeadsListView from '@/components/ListViews/LeadsListView.vue'
import { formatDate, timeAgo } from '@/utils'
import { getView } from '@/utils/view'
import { useDocument } from '@/data/document'
import { getSettings } from '@/stores/settings'
import { getMeta } from '@/stores/meta'
import { usersStore } from '@/stores/users.js'
import { statusesStore } from '@/stores/statuses'
import {
  Breadcrumbs,
  Avatar,
  Tabs,
  createResource,
  usePageMeta,
  toast,
} from 'frappe-ui'
import { ref, computed, h, watch } from 'vue'
import { useRoute } from 'vue-router'

const { brand } = getSettings()

const { getUser } = usersStore()
const { getLeadStatus } = statusesStore()
const { doctypeMeta } = getMeta('CRM Sales')

const props = defineProps({
  salesTeamId: {
    type: String,
    required: true,
  },
})

const route = useRoute()

const errorTitle = ref('')
const errorMessage = ref('')

const { document: salesTeam } = useDocument('CRM Sales', props.salesTeamId)

const breadcrumbs = computed(() => {
  let items = [{ label: __('Sales Team'), route: { name: 'SalesTeam' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(route.query.view, route.query.viewType, 'CRM Sales')
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'SalesTeam',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: title.value,
    route: { name: 'SalesTeamDetail', params: { salesTeamId: props.salesTeamId } },
  })
  return items
})

const title = computed(() => {
  let t = doctypeMeta['CRM Sales']?.title_field || 'name'
  return salesTeam.doc?.[t] || props.salesTeamId
})

usePageMeta(() => {
  return {
    title: title.value,
    icon: brand.favicon,
  }
})
const showDeleteLinkedDocModal = ref(false)

const tabIndex = ref(0)
const tabs = [
  {
    label: 'Leads',
    icon: h(LeadsIcon, { class: 'h-4 w-4' }),
    count: computed(() => rowsCurrentMonth.value.length),
  },
  {
    label: 'All Leads',
    icon: h(LeadsIcon, { class: 'h-4 w-4' }),
    count: computed(() => rows.value.length),
  },
  {
    label: 'List FID',
    icon: h(LeadsIcon, { class: 'h-4 w-4' }),
    count: computed(() => fidData.value.length),
  },
]

const leads = createResource({
  url: 'crm.api.sales_team.get_linked_leads',
  cache: ['leads', props.salesTeamId],
  params: {
    sales_team: props.salesTeamId,
  },
  auto: true,
})

const rows = computed(() => {
  if (!leads.data || leads.data == []) return []

  return leads.data.map((row) => getLeadRowObject(row))
})
const rowsCurrentMonth = computed(() => {
  if (!leads.data || leads.data.length === 0) return []
  const now = new Date()
  const m = now.getMonth()
  const y = now.getFullYear()
  return leads.data
    .filter((lead) => {
      const d = new Date(lead.creation || lead.created || lead.modified)
      return d.getMonth() === m && d.getFullYear() === y
    })
    .map((row) => getLeadRowObject(row))
})

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_sidepanel_sections',
  cache: ['sidePanelSections', 'CRM Sales'],
  params: { doctype: 'CRM Sales' },
  auto: true,
})

const fidList = createResource({
  url: 'crm.api.sales_team.get_fid',
  auto: false,
})

const fidData = computed(() => {
  // Normalisasi data agar tetap tampil walau backend mengembalikan object { nasabah: [...] }
  const d = fidList.data
  if (Array.isArray(d)) return d
  if (d && Array.isArray(d.nasabah)) return d.nasabah
  return []
})

const fidColumns = computed(() => {
  if (fidData.value.length === 0) return []
  const sample = fidData.value[0] || {}
  const keys = Object.keys(sample).filter((k) => {
    const v = sample[k]
    return ['string', 'number', 'boolean'].includes(typeof v) || v === null
  })
  return keys.slice(0, 8)
})

function formatCell(value) {
  if (value === null || value === undefined) return ''
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value)
    } catch (e) {
      return String(value)
    }
  }
  return String(value)
}

watch(tabIndex, (i) => {
  const t = tabs[i]
  if (t?.label === 'List FID' && !fidList.data && !fidList.loading) {
    fidList.reload && fidList.reload()
  }
})

const { getFormattedCurrency } = getMeta('CRM Lead')

const columns = computed(() => leadColumns)

function getLeadRowObject(lead) {
  return {
    name: lead.name,
    lead_name: {
      label: lead.lead_name,
      image: lead.image,
      image_label: lead.first_name,
    },
    organization: lead.organization,
    status: {
      label: lead.status,
      color: getLeadStatus(lead.status)?.color,
    },
    email: lead.email,
    mobile_no: lead.mobile_no,
    lead_owner: {
      label: lead.lead_owner && getUser(lead.lead_owner).full_name,
      ...(lead.lead_owner && getUser(lead.lead_owner)),
    },
    modified: {
      label: formatDate(lead.modified),
      timeAgo: __(timeAgo(lead.modified)),
    },
  }
}

const leadColumns = [
  {
    label: __('Name'),
    key: 'lead_name',
    width: '12rem',
  },
  {
    label: __('Organization'),
    key: 'organization',
    width: '10rem',
  },
  {
    label: __('Status'),
    key: 'status',
    width: '8rem',
  },
  {
    label: __('Email'),
    key: 'email',
    width: '12rem',
  },
  {
    label: __('Mobile no'),
    key: 'mobile_no',
    width: '11rem',
  },
  {
    label: __('Lead owner'),
    key: 'lead_owner',
    width: '10rem',
  },
  {
    label: __('Last modified'),
    key: 'modified',
    width: '8rem',
  },
]
</script>