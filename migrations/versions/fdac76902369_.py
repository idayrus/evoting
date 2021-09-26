"""empty message

Revision ID: fdac76902369
Revises: c18de593d107
Create Date: 2021-09-25 16:12:22.932336

"""
from alembic import op
import sqlalchemy as sa
import app.helper


# revision identifiers, used by Alembic.
revision = 'fdac76902369'
down_revision = 'c18de593d107'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('candidate',
    sa.Column('id_', app.helper.sqlalchemy.ObjectIDField(length=32), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Integer(), nullable=True),
    sa.Column('number', sa.String(length=128), nullable=False),
    sa.Column('leader_name', sa.Text(), nullable=False),
    sa.Column('deputy_name', sa.Text(), nullable=True),
    sa.Column('photo', sa.Text(), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('campaign_video', sa.Text(), nullable=True),
    sa.Column('campaign_info', sa.Text(), nullable=True),
    sa.Column('extra_info', app.helper.sqlalchemy.DictField(), nullable=True),
    sa.PrimaryKeyConstraint('id_')
    )
    op.create_index(op.f('ix_candidate_deleted'), 'candidate', ['deleted'], unique=False)
    op.create_index(op.f('ix_candidate_id_'), 'candidate', ['id_'], unique=False)
    op.create_table('voter',
    sa.Column('id_', app.helper.sqlalchemy.ObjectIDField(length=32), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Integer(), nullable=True),
    sa.Column('id_number', sa.String(length=128), nullable=False),
    sa.Column('pin', sa.Integer(), nullable=True),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('gender', sa.Integer(), nullable=True),
    sa.Column('birthdate', sa.String(length=64), nullable=True),
    sa.Column('contact', sa.Text(), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('extra_info', app.helper.sqlalchemy.DictField(), nullable=True),
    sa.PrimaryKeyConstraint('id_')
    )
    op.create_index(op.f('ix_voter_deleted'), 'voter', ['deleted'], unique=False)
    op.create_index(op.f('ix_voter_id_'), 'voter', ['id_'], unique=False)
    op.create_table('voter_ballot',
    sa.Column('id_', app.helper.sqlalchemy.ObjectIDField(length=32), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Integer(), nullable=True),
    sa.Column('candidate_id', app.helper.sqlalchemy.ObjectIDField(length=32), nullable=False),
    sa.Column('voter_id', app.helper.sqlalchemy.ObjectIDField(length=32), nullable=False),
    sa.ForeignKeyConstraint(['candidate_id'], ['candidate.id_'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['voter_id'], ['voter.id_'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_')
    )
    op.create_index(op.f('ix_voter_ballot_deleted'), 'voter_ballot', ['deleted'], unique=False)
    op.create_index(op.f('ix_voter_ballot_id_'), 'voter_ballot', ['id_'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_voter_ballot_id_'), table_name='voter_ballot')
    op.drop_index(op.f('ix_voter_ballot_deleted'), table_name='voter_ballot')
    op.drop_table('voter_ballot')
    op.drop_index(op.f('ix_voter_id_'), table_name='voter')
    op.drop_index(op.f('ix_voter_deleted'), table_name='voter')
    op.drop_table('voter')
    op.drop_index(op.f('ix_candidate_id_'), table_name='candidate')
    op.drop_index(op.f('ix_candidate_deleted'), table_name='candidate')
    op.drop_table('candidate')
    # ### end Alembic commands ###