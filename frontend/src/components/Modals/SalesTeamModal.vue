<template>
  <Dialog v-model="show" :options="{ size: 'xl' }">
    <template #body>
      <div class="bg-surface-modal px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
              {{ __('New Sales Team Member') }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button
              v-if="isManager() && !isMobileView"
              variant="ghost"
              class="w-7"
              @click="openQuickEntryModal"
            >
              <template #icon>
                <EditIcon />
              </template>
            </Button>
            <Button variant="ghost" class="w-7" @click="show = false">
              <template #icon>
                <FeatherIcon name="x" class="size-4" />
              </template>
            </Button>
          </div>
        </div>
        <FieldLayout
          v-if="tabs.data?.length"
          :tabs="tabs.data"
          :data="_salesTeam.doc"
          doctype="CRM Sales"
        />
      </div>
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="space-y-2">
          <Button
            class="w-full"
            variant="solid"
            :label="__('Create')"
            :loading="loading"
            @click="createSalesTeam"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import { usersStore } from '@/stores/users'
import { isMobileView } from '@/composables/settings'
import {
  showQuickEntryModal,
  quickEntryProps,
} from '@/composables/modals'
import { useDocument } from '@/data/document'
import { capture } from '@/telemetry'
import { call, createResource } from 'frappe-ui'
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  salesTeam: {
    type: Object,
    default: {},
  },
  options: {
    type: Object,
    default: {
      redirect: true,
      afterInsert: () => {},
    },
  },
})

const { isManager } = usersStore()

const router = useRouter()
const show = defineModel()

const loading = ref(false)

const { document: _salesTeam, triggerOnBeforeCreate } = useDocument('CRM Sales')

async function createSalesTeam() {
  await triggerOnBeforeCreate?.()

  const doc = await call('frappe.client.insert', {
    doc: {
      doctype: 'CRM Sales',
      ..._salesTeam.doc,
    },
  })
  if (doc.name) {
    capture('sales_team_created')
    handleSalesTeamUpdate(doc)
  }
}

function handleSalesTeamUpdate(doc) {
  props.salesTeam?.reload?.()
  if (doc.name && props.options.redirect) {
    router.push({
      name: 'SalesTeamDetail',
      params: { salesTeamId: doc.name },
    })
  }
  show.value = false
  props.options.afterInsert && props.options.afterInsert(doc)
}

const tabs = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['QuickEntry', 'CRM Sales'],
  params: { doctype: 'CRM Sales', type: 'Quick Entry' },
  auto: true,
})

onMounted(() => {
  _salesTeam.doc = {}
  Object.assign(_salesTeam.doc, props.salesTeam.data || props.salesTeam)
})

function openQuickEntryModal() {
  showQuickEntryModal.value = true
  quickEntryProps.value = { doctype: 'CRM Sales' }
  nextTick(() => (show.value = false))
}
</script>

<style scoped>
:deep(:has(> .dropdown-button)) {
  width: 100%;
}
</style>