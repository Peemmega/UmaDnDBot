"""Extensible registry for immediate skill effects.

The registry intentionally receives game operations through a context instead
of importing ``game_manager``.  This keeps effect handlers independent from
the transport/lifecycle layer and avoids circular imports.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Callable

from utils.race.runtime_stamina import (
    get_runtime_stamina_snapshot,
    set_runtime_stamina,
    sync_runtime_stamina,
)
from utils.race.stamina_rules import calculate_percent_stamina_amount


@dataclass
class SkillEffectContext:
    channel_id: int
    user_id: object
    game: dict
    player: dict
    skill: dict
    targets: list[tuple[object, dict]]
    skills: dict
    update_player_score: Callable[[int, object, int], tuple[bool, Any]]
    apply_race_stat_changes: Callable[[dict, dict, dict], dict]
    format_player_reference: Callable[[object, dict | None], str]
    increase_speed: Callable[[dict, dict, int], None]
    apply_pending_lane_change_now: Callable[[int, object], tuple[bool, Any]]
    can_force_rush_targets: Callable[[int, list[tuple[object, dict]]], tuple[bool, str | None]]
    use_rush: Callable[[int, object], tuple[bool, Any]]
    execute_skill_core: Callable[..., tuple[bool, dict | str]]


@dataclass
class SkillEffectResult:
    texts: list[str] = field(default_factory=list)
    error: str | None = None


EffectHandler = Callable[[SkillEffectContext, dict], SkillEffectResult]
EffectValidator = Callable[[SkillEffectContext, dict], str | None]


class SkillEffectRegistry:
    """Map effect types to their validation and execution handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, EffectHandler] = {}
        self._validators: dict[str, EffectValidator] = {}

    def register(self, *effect_types: str):
        def decorator(handler: EffectHandler) -> EffectHandler:
            for effect_type in effect_types:
                self._handlers[effect_type] = handler
            return handler

        return decorator

    def register_validator(self, effect_type: str):
        def decorator(validator: EffectValidator) -> EffectValidator:
            self._validators[effect_type] = validator
            return validator

        return decorator

    def validate(self, context: SkillEffectContext, effects: list[dict]) -> str | None:
        for effect in effects:
            validator = self._validators.get(effect.get("type"))
            if validator:
                reason = validator(context, effect)
                if reason:
                    return reason
        return None

    def execute(self, context: SkillEffectContext, effect: dict) -> SkillEffectResult:
        handler = self._handlers.get(effect.get("type"))
        return handler(context, effect) if handler else SkillEffectResult()


SKILL_EFFECTS = SkillEffectRegistry()


def _self_or_targets(context: SkillEffectContext) -> list[tuple[object, dict]]:
    return context.targets or [(context.user_id, context.player)]


def _stamina_change(player: dict, value: int | float) -> int:
    snapshot = sync_runtime_stamina(player)
    return calculate_percent_stamina_amount(snapshot["max_stamina"], value)


@SKILL_EFFECTS.register("recover_stamina", "self_heal_stamina")
def _heal_stamina(context: SkillEffectContext, effect: dict) -> SkillEffectResult:
    gain = _stamina_change(context.player, effect.get("value", 0))
    set_runtime_stamina(
        context.player,
        context.player.get("stamina_stat", 0),
        context.player.get("stamina_left", 0) + gain,
    )
    return SkillEffectResult([f"ฟื้นฟู STA ตัวเอง +{gain}"])


@SKILL_EFFECTS.register("modify_current_speed")
def _modify_current_speed(context: SkillEffectContext, effect: dict) -> SkillEffectResult:
    value = effect.get("value", 0)
    context.increase_speed(context.game, context.player, value)
    return SkillEffectResult([f"เร่งความเร็วขึ้น {value} ระดับ"])


@SKILL_EFFECTS.register("modify_race_stats")
def _modify_race_stats(context: SkillEffectContext, effect: dict) -> SkillEffectResult:
    texts: list[str] = []
    for target_id, target in _self_or_targets(context):
        stamina_before = get_runtime_stamina_snapshot(target)
        changes = context.apply_race_stat_changes(target, context.game, effect)
        if not changes:
            continue
        stamina_after = get_runtime_stamina_snapshot(target)
        target_name = (
            "ตัวเอง"
            if target_id == context.user_id
            else context.format_player_reference(target_id, target)
        )
        change_text = ", ".join(f"{stat.title()} {delta:+}" for stat, delta in changes.items())
        stamina_text = ""
        if "stamina" in changes:
            stamina_text = (
                f" | Stamina {stamina_before['current_stamina']}/"
                f"{stamina_before['max_stamina']} → {stamina_after['current_stamina']}/"
                f"{stamina_after['max_stamina']}"
            )
        texts.append(f"ปรับ Stats ของ{target_name}: {change_text}{stamina_text}")
        context.skill.setdefault("_race_stat_changes", []).append(
            {
                "target_id": str(target_id),
                "target_name": target_name,
                "changes": changes,
                "stamina_before": stamina_before,
                "stamina_after": stamina_after,
            }
        )
    return SkillEffectResult(texts)


@SKILL_EFFECTS.register("flat_total")
def _flat_total(context: SkillEffectContext, effect: dict) -> SkillEffectResult:
    value = effect.get("value", 0)
    sign = "+" if value >= 0 else ""
    texts: list[str] = []
    for target_id, target in _self_or_targets(context):
        success, _ = context.update_player_score(context.channel_id, target_id, value)
        if not success:
            continue
        if target_id == context.user_id:
            texts.append(f"ปรับคะแนนตัวเองทันที {sign}{value}")
        else:
            texts.append(
                f"ปรับคะแนน {context.format_player_reference(target_id, target)} ทันที {sign}{value}"
            )
    return SkillEffectResult(texts)


@SKILL_EFFECTS.register("reduce_stamina")
def _reduce_stamina(context: SkillEffectContext, effect: dict) -> SkillEffectResult:
    if not context.targets:
        return SkillEffectResult()

    texts: list[str] = []
    for target_id, target in context.targets:
        loss = _stamina_change(target, effect.get("value", 0))
        set_runtime_stamina(
            target,
            target.get("stamina_stat", 0),
            target.get("stamina_left", 0) - loss,
        )
        texts.append(
            f"ลด STA ของ {context.format_player_reference(target_id, target)} -{loss}"
        )
    return SkillEffectResult(texts)


@SKILL_EFFECTS.register("resolve_pending_lane_now")
def _resolve_pending_lane_now(context: SkillEffectContext, effect: dict) -> SkillEffectResult:
    success, result = context.apply_pending_lane_change_now(context.channel_id, context.user_id)
    if not success:
        return SkillEffectResult(error=result)
    if result.get("lane_changed"):
        text = f"เปลี่ยน Lane ทันที {result['previous_lane']} -> {result['current_lane']}"
    else:
        text = f"ยืนยัน Lane {result['current_lane']} ทันที"
    return SkillEffectResult([text])


@SKILL_EFFECTS.register("activate_random_equipped_skills")
def _activate_random_equipped_skills(
    context: SkillEffectContext, effect: dict
) -> SkillEffectResult:
    max_cost = effect.get("max_cost", 80)
    count = effect.get("count", 2)
    equipped = list(dict.fromkeys(skill_id for skill_id in context.player.get("skills", {}).values() if skill_id))
    eligible = [
        skill_id
        for skill_id in equipped
        if skill_id in context.skills
        and context.skills[skill_id].get("cost", 0) <= max_cost
        and not any(
            candidate.get("type") == "activate_random_equipped_skills"
            for candidate in context.skills[skill_id].get("effects", [])
        )
    ]
    selected = random.sample(eligible, min(count, len(eligible)))
    if not selected:
        return SkillEffectResult(
            [f"ไม่มีสกิลติดตั้งที่ใช้สุ่มได้ (Cost ไม่เกิน {max_cost})"]
        )

    activations = []
    for skill_id in selected:
        activated, payload = context.execute_skill_core(
            context.channel_id,
            context.user_id,
            skill_id,
            consume_cost=False,
            ignore_cooldown=True,
            ignore_trigger=True,
            apply_cooldown=False,
        )
        if activated:
            activations.append(
                {
                    "skill_id": skill_id,
                    "name": payload["skill_name"],
                    "result_texts": payload.get("result_texts", []),
                }
            )

    if not activations:
        return SkillEffectResult()
    context.skill.setdefault("_random_activations", []).extend(activations)
    texts = ["สุ่มใช้สกิลทันที:"]
    for activation in activations:
        texts.append(f"• {activation['name']}")
        texts.extend(f"  └ {text}" for text in activation["result_texts"])
    return SkillEffectResult(texts)


@SKILL_EFFECTS.register("apply_debuff_next_turn")
def _apply_debuff_next_turn(context: SkillEffectContext, effect: dict) -> SkillEffectResult:
    if not context.targets:
        return SkillEffectResult()

    stat = effect.get("stat", "flat_total")
    value = effect.get("value", 0)
    texts: list[str] = []
    for target_id, target in context.targets:
        reference = context.format_player_reference(target_id, target)
        if stat == "flat_total":
            target["next_roll_flat_bonus"] = target.get("next_roll_flat_bonus", 0) + value
            texts.append(f"ใส่ดีบัฟให้ {reference} เทิร์นหน้า Flat {value}")
        elif stat == "cap":
            target["next_roll_cap_bonus"] = target.get("next_roll_cap_bonus", 0) + value
            texts.append(f"ใส่ดีบัฟให้ {reference} เทิร์นหน้า Cap {value}")
    return SkillEffectResult(texts)


@SKILL_EFFECTS.register_validator("force_rush")
def _validate_force_rush(context: SkillEffectContext, effect: dict) -> str | None:
    valid, reason = context.can_force_rush_targets(context.channel_id, context.targets)
    return None if valid else reason


@SKILL_EFFECTS.register("force_rush")
def _force_rush(context: SkillEffectContext, effect: dict) -> SkillEffectResult:
    if not context.targets:
        return SkillEffectResult()
    texts: list[str] = []
    for target_id, target in context.targets:
        success, payload = context.use_rush(context.channel_id, target_id)
        reference = context.format_player_reference(target_id, target)
        if success:
            texts.append(f"บังคับ {reference} ใช้ Rush สำเร็จ")
        else:
            texts.append(f"บังคับ {reference} ใช้ Rush ไม่สำเร็จ ({payload})")
    return SkillEffectResult(texts)


@SKILL_EFFECTS.register("modify_gold_range")
def _modify_gold_range(context: SkillEffectContext, effect: dict) -> SkillEffectResult:
    value = effect.get("value", 0)
    context.player["gold_range_bonus_this_turn"] = (
        context.player.get("gold_range_bonus_this_turn", 0) + value
    )
    return SkillEffectResult([f"เพิ่มระยะตรวจ Gold +{value}"])


@SKILL_EFFECTS.register("modify_gold_lane_range")
def _modify_gold_lane_range(context: SkillEffectContext, effect: dict) -> SkillEffectResult:
    value = effect.get("value", 0)
    context.player["gold_lane_bonus_this_turn"] = (
        context.player.get("gold_lane_bonus_this_turn", 0) + value
    )
    return SkillEffectResult([f"เพิ่มระยะตรวจเลน Gold +{value}"])


@SKILL_EFFECTS.register("modify_enemy_gold_range")
def _modify_enemy_gold_range(context: SkillEffectContext, effect: dict) -> SkillEffectResult:
    if not context.targets:
        return SkillEffectResult()
    value = abs(effect.get("value", 0))
    texts: list[str] = []
    for target_id, target in context.targets:
        target["enemy_gold_range_penalty_next_turn"] = (
            target.get("enemy_gold_range_penalty_next_turn", 0) + value
        )
        texts.append(
            f"ลดระยะตรวจ Gold ของ {context.format_player_reference(target_id, target)} {value}"
        )
    return SkillEffectResult(texts)


@SKILL_EFFECTS.register("modify_enemy_gold_lane_range")
def _modify_enemy_gold_lane_range(context: SkillEffectContext, effect: dict) -> SkillEffectResult:
    if not context.targets:
        return SkillEffectResult()
    value = abs(effect.get("value", 0))
    texts: list[str] = []
    for target_id, target in context.targets:
        target["enemy_gold_lane_penalty_next_turn"] = (
            target.get("enemy_gold_lane_penalty_next_turn", 0) + value
        )
        texts.append(
            f"ลดระยะตรวจเลน Gold ของ {context.format_player_reference(target_id, target)} {value}"
        )
    return SkillEffectResult(texts)


def apply_registered_skill_effects(
    context: SkillEffectContext, effects: list[dict]
) -> tuple[bool, list[str] | str]:
    """Validate and apply effects in order, preserving the skill's atomic checks."""
    validation_error = SKILL_EFFECTS.validate(context, effects)
    if validation_error:
        return False, validation_error

    texts: list[str] = []
    for effect in effects:
        result = SKILL_EFFECTS.execute(context, effect)
        if result.error:
            return False, result.error
        texts.extend(result.texts)
    return True, texts
