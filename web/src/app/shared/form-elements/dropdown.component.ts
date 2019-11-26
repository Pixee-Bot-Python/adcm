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
import { Component, OnInit, Input } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { FieldOptions } from '@app/core/types';
import { Observable, of } from 'rxjs';

@Component({
  selector: 'app-fields-dropdown',
  template: `
    <ng-container [formGroup]="form">
      <label>{{ field.label }}:</label>
      <mat-form-field class="full-width">
        <mat-select [(value)]="field.value" [formControlName]="field.key">
          <mat-option *ngFor="let option of options$ | async" [value]="option.id">{{ option.name }}</mat-option>
        </mat-select>
      </mat-form-field>
      <span class="info"><mat-icon *ngIf="field.description" matSuffix [appTooltip]="field.description">info_outline</mat-icon></span>
    </ng-container>
  `,
  styleUrls: ['./scss/fields.component.scss'],
})
export class DropdownComponent implements OnInit {
  @Input() form: FormGroup;
  @Input() field: FieldOptions;
  options$: Observable<{ id: number | string; name: string }[]>;

  ngOnInit() {
    if (this.field.limits) {
      const o = Object.entries<string | number>(this.field.limits.option).map(e => ({
        id: String(e[1]),
        name: e[0],
      }));
      this.options$ = of(o);
    }
  }
}
