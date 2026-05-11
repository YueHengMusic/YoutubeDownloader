<template>
  <div ref="root_ref" class="ui_select">
    <button
      type="button"
      class="ui_select_trigger"
      :class="{ open: is_open, disabled }"
      :disabled="disabled"
      @click="toggle_menu"
    >
      <span>{{ selected_label }}</span>
      <span class="ui_select_arrow" aria-hidden="true">⌄</span>
    </button>

    <div v-if="is_open" class="ui_select_menu">
      <button
        v-for="option in options"
        :key="option.value"
        type="button"
        class="ui_select_option"
        :class="{ selected: option.value === modelValue }"
        :disabled="option.disabled"
        @click="choose_option(option.value)"
      >
        {{ option.label }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

/**
 * 自定义下拉选择组件（替代原生 select）：
 * - 目标：避免系统原生下拉弹层样式与页面设计冲突；
 * - 行为：点击触发器展开，选择后回填并关闭，点击外部自动关闭；
 * - 组件职责：仅处理展示与交互，不关心业务语义。
 */
export type UiSelectOption = {
  value: string;
  label: string;
  disabled?: boolean;
};

const props = withDefaults(
  defineProps<{
    modelValue: string;
    options: UiSelectOption[];
    disabled?: boolean;
  }>(),
  {
    disabled: false
  }
);

const emit = defineEmits<{
  (event: "update:modelValue", value: string): void;
}>();

const is_open = ref(false);
const root_ref = ref<HTMLElement | null>(null);

const selected_label = computed(() => {
  const selected_option = props.options.find((option) => option.value === props.modelValue);
  return selected_option?.label ?? "";
});

function toggle_menu() {
  if (props.disabled) return;
  is_open.value = !is_open.value;
}

function choose_option(value: string) {
  emit("update:modelValue", value);
  is_open.value = false;
}

function handle_pointer_down(event: MouseEvent) {
  const target = event.target as Node | null;
  if (!target) return;
  if (root_ref.value?.contains(target)) return;
  is_open.value = false;
}

onMounted(() => {
  window.addEventListener("mousedown", handle_pointer_down);
});

onBeforeUnmount(() => {
  window.removeEventListener("mousedown", handle_pointer_down);
});
</script>

<style scoped>
.ui_select {
  position: relative;
  width: 100%;
}

.ui_select_trigger {
  width: 100%;
  height: var(--field_height);
  border: 1px solid var(--hairline);
  border-radius: 9999px;
  padding: 0 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--canvas);
  color: var(--ink);
  cursor: pointer;
}

.ui_select_trigger.open {
  border-color: var(--ink);
  box-shadow: 0 0 0 3px var(--focus-ring);
}

.ui_select_trigger.disabled {
  background: var(--surface-soft);
  color: var(--mute);
  cursor: not-allowed;
}

.ui_select_arrow {
  color: var(--body);
  font-size: 16px;
  line-height: 1;
}

.ui_select_menu {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  z-index: 20;
  border: 1px solid var(--hairline);
  border-radius: 12px;
  background: var(--canvas);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ui_select_option {
  height: var(--control_height);
  border: 0;
  border-radius: 8px;
  padding: 0 12px;
  background: transparent;
  text-align: left;
  color: var(--ink);
  cursor: pointer;
}

.ui_select_option:hover {
  background: var(--surface-soft);
}

.ui_select_option.selected {
  background: #f3f4f6;
}

.ui_select_option:disabled {
  color: var(--mute);
  cursor: not-allowed;
}

@media (max-width: 560px) {
  .ui_select_trigger {
    height: var(--field_height_compact);
  }
  .ui_select_option {
    height: var(--control_height_compact);
  }
}
</style>
