<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('procedures', function (Blueprint $table) {
            $table->id();
            $table->string('procedure_reference', 128)->nullable(); // BT-22-Procedure
            $table->foreignId('buyer_id')->nullable()->constrained('organizations')->nullOnDelete();
            $table->string('procedure_type', 32)->nullable();   // BT-105-Procedure
            $table->string('contract_type', 32)->nullable();    // BT-23-Procedure (works, services, supplies)
            $table->string('main_cpv', 10)->nullable();          // BT-262-Procedure
            $table->foreign('main_cpv')->references('code')->on('cpv_codes')->nullOnDelete();
            $table->decimal('total_value', 14, 2)->nullable();   // BT-27-Procedure_value
            $table->char('currency', 3)->nullable();
            $table->string('nuts_code', 10)->nullable();         // BT-5071-Procedure
            $table->text('title')->nullable();                    // BT-21-Procedure
            $table->text('description')->nullable();              // BT-24-Procedure
            $table->text('buyer_profile_url')->nullable();       // BT-508-Procedure-Buyer
            $table->timestamps();
            $table->jsonb('extra_fields')->nullable();
            $table->unique(['procedure_reference', 'buyer_id']);
            $table->index('buyer_id');
            $table->text('place_of_performance')->nullable()->after('nuts_code');
            $table->index('main_cpv');
            $table->index('nuts_code');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('procedures');
    }
};