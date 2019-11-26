// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
import { Component, Directive, Input, OnInit } from '@angular/core';
import { AbstractControl, FormArray, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { FieldOptions } from '@app/core/types';

@Directive({
  selector: '[appBaseMapList]'
})
export class BaseMapListDirective implements OnInit {
  @Input() form: FormGroup;
  @Input() field: FieldOptions;
  asList: boolean;
  items = new FormArray([]);
  entry: AbstractControl[];

  constructor(private fb: FormBuilder) {}

  ngOnInit() {
    if (!Object.keys(this.field.value).length) this.form.controls[this.field.key].setValue('');
    this.reload();
    this.items.valueChanges.subscribe((a: { key: string; value: string }[]) => this.prepare(a));
    // this.entry = [...this.items.controls];
  }

  get isValid() {
    const field = this.form.controls[this.field.key];
    return field.disabled || (field.valid && (field.dirty || field.touched));
  }

  hasError(name: string) {
    return this.form.controls[this.field.key].hasError(name);
  }

  prepare(a: { key: string; value: string }[]) {
    let value = this.asList
      ? a.map(b => b.value).filter(c => c)
      : a.length
      ? a.reduce((p, c) => ({ ...p, [c.key]: c.value }), {})
      : null;

    if (value && this.asList) value = (value as Array<string>).length ? value : null;

    this.form.controls[this.field.key].setValue(value);
  }

  reload() {
    this.items.controls = [];
    const fieldValue = this.field.value as Object;
    Object.keys(fieldValue).forEach(a =>
      this.items.push(this.fb.group({ key: [a, Validators.required], value: fieldValue[a] }))
    );
  }

  add() {
    const group = this.fb.group({ key: ['', Validators.required], value: '' });
    this.items.push(group);
    group.controls['key'].markAsTouched();
  }

  check(item: FormGroup) {
    return item.controls['key'].hasError('required');
  }

  clear(i: number) {
    this.items.removeAt(i);
  }
}

@Component({
  selector: 'app-fields-list',
  templateUrl: './map-list.template.html',
  styleUrls: ['./scss/map.component.scss'],
})
export class FieldListComponent extends BaseMapListDirective {
  asList = true;
}

@Component({
  selector: 'app-fields-map',
  templateUrl: './map-list.template.html',
  styleUrls: ['./scss/map.component.scss'],
})
export class FieldMapComponent extends BaseMapListDirective {
  asList = false;
}
