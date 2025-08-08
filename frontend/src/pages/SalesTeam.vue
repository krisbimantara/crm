<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="SalesTeam" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="salesTeamListView?.customListActions"
        :actions="salesTeamListView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        @click="showSalesTeamModal = true"
      >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="salesTeam"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="CRM Sales"
  />
  <SalesTeamListView
    ref="salesTeamListView"
    v-if="salesTeam.data && rows.length"
    v-model="salesTeam.data.page_length_count"
    v-model:list="salesTeam"
    :rows="rows"
    :columns="salesTeam.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: salesTeam.data.row_count,
      totalCount: salesTeam.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
    @selectionsChanged="
      (selections) => viewControls.updateSelections(selections)
    "
  />
  <div
    v-else-if="salesTeam.data"
    class="flex h-full items-center justify-center"
  >
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4"
    >
      <SalesTeamIcon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Sales Team')]) }}</span>
      <Button :label="__('Create')" @click="showSalesTeamModal = true">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </div>
  </div>
  <SalesTeamModal
    v-if="showSalesTeamModal"
    v-model="showSalesTeamModal"
    :salesTeam="{}"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import SalesTeamIcon from '@/components/Icons/SalesTeamIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import SalesTeamModal from '@/components/Modals/SalesTeamModal.vue'
import SalesTeamListView from '@/components/ListViews/SalesTeamListView.vue'
import ViewControls from '@/components/ViewControls.vue'
import { getMeta } from '@/stores/meta'
import { formatDate, timeAgo } from '@/utils'
import { ref, computed } from 'vue'

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta('CRM Sales')

const showSalesTeamModal = ref(false)

const salesTeamListView = ref(null)

// salesTeam data is loaded in the ViewControls component
const salesTeam = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

const rows = computed(() => {
  if (
    !salesTeam.value?.data?.data ||
    !['list', 'group_by'].includes(salesTeam.value.data.view_type)
  )
    return []
  return salesTeam.value?.data.data.map((salesPerson) => {
    let _rows = {}
    salesTeam.value?.data.rows.forEach((row) => {
      _rows[row] = salesPerson[row]

      let fieldType = salesTeam.value?.data.columns?.find(
        (col) => (col.key || col.value) == row,
      )?.type

      if (
        fieldType &&
        ['Date', 'Datetime'].includes(fieldType) &&
        !['modified', 'creation'].includes(row)
      ) {
        _rows[row] = formatDate(salesPerson[row], '', true, fieldType == 'Datetime')
      }

      if (fieldType && fieldType == 'Currency') {
        _rows[row] = getFormattedCurrency(row, salesPerson)
      }

      if (fieldType && fieldType == 'Float') {
        _rows[row] = getFormattedFloat(row, salesPerson)
      }

      if (fieldType && fieldType == 'Percent') {
        _rows[row] = getFormattedPercent(row, salesPerson)
      }

      if (row == 'nama') {
        _rows[row] = {
          label: salesPerson.nama,
        }
      } else if (row == 'user_id') {
        _rows[row] = {
          label: salesPerson.user_id,
        }
      } else if (row == 'cabang') {
        _rows[row] = {
          label: salesPerson.cabang,
        }
      } else if (['modified', 'creation'].includes(row)) {
        _rows[row] = {
          label: formatDate(salesPerson[row]),
          timeAgo: __(timeAgo(salesPerson[row])),
        }
      }
    })
    return _rows
  })
})
</script>