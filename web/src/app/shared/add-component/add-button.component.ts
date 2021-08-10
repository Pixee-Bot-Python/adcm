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
import { Component, EventEmitter, Inject, Input, OnDestroy, Output } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';

import { DialogComponent } from '../components/dialog.component';
import { BaseDirective } from '../directives/base.directive';
import { AddFormComponent } from './add-form.component';
import { ADD_SERVICE_PROVIDER, IAddService } from '@app/shared/add-component/add-service-token';
import { LIST_SERVICE_PROVIDER } from '@app/shared/components/list/list-service-token';
import { ConfigGroupHostListService } from '@app/config-groups/service/config-group-host-list.service';
import { ConfigGroupHostAddService } from '@app/config-groups/service/config-group-host-add.service';

@Component({
  selector: 'app-add-button',
  template: `
    <ng-container *ngIf="!asIcon; else icon">
      <button [appForTest]="'create-btn'" mat-raised-button color="accent" (click)="showForm()">
        <mat-icon>library_add</mat-icon>&nbsp;<ng-content></ng-content>
      </button>
    </ng-container>
    <ng-template #icon>
      <button [appForTest]="'create-btn'" mat-icon-button color="primary" (click)="showForm()">
        <mat-icon>add</mat-icon>
      </button>
    </ng-template>
  `,
  styles: ['button {margin-right: 6px;}'],
  providers: [
    { provide: LIST_SERVICE_PROVIDER, useClass: ConfigGroupHostListService },
    { provide: ADD_SERVICE_PROVIDER, useClass: ConfigGroupHostAddService }
  ],
})
export class AddButtonComponent extends BaseDirective implements OnDestroy {
  @Input() asIcon = false;
  @Input() name: string;
  @Output() added = new EventEmitter();

  constructor(@Inject(ADD_SERVICE_PROVIDER) private service: IAddService,
              private dialog: MatDialog) {
    super();
  }

  showForm() {
    const model = this.service.model(this.name);
    const name = model.title || model.name;
    const title = ['cluster', 'provider', 'host'];
    this.dialog.open(DialogComponent, {
      width: '75%',
      maxWidth: '1400px',
      data: {
        title: `${title.includes(name) ? 'Create' : 'Add'} ${name}`,
        component: AddFormComponent,
        model,
      },
    });
  }
}
